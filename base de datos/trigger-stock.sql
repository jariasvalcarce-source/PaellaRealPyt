-- =====================================================
-- TRIGGER: descontar stock automáticamente al preparar pedido
-- Se dispara cuando estado_pedido cambia a 'preparando'
-- =====================================================

DELIMITER $$

CREATE TRIGGER trg_descontar_stock
AFTER UPDATE ON pedidos
FOR EACH ROW
BEGIN
    -- Descontar stock cuando el pedido pasa a 'preparando'
    IF NEW.estado_pedido = 'preparando' AND OLD.estado_pedido IN ('pendiente', 'confirmado') THEN

        -- Descontar stock de cada producto usado en el pedido, convirtiendo unidades
        UPDATE productos pr
        JOIN (
            SELECT r.id_produ_fk,
                   SUM(
                       CASE 
                           -- gramo -> kilogramo
                           WHEN LOWER(TRIM(uo.nom_uni_medi)) = 'gramo' AND LOWER(TRIM(ud.nom_uni_medi)) = 'kilogramo' THEN r.cantidad_reque * 0.001
                           -- mililitro -> litro
                           WHEN LOWER(TRIM(uo.nom_uni_medi)) = 'mililitro' AND LOWER(TRIM(ud.nom_uni_medi)) = 'litro' THEN r.cantidad_reque * 0.001
                           -- kilogramo -> gramo
                           WHEN LOWER(TRIM(uo.nom_uni_medi)) = 'kilogramo' AND LOWER(TRIM(ud.nom_uni_medi)) = 'gramo' THEN r.cantidad_reque * 1000.0
                           -- litro -> mililitro
                           WHEN LOWER(TRIM(uo.nom_uni_medi)) = 'litro' AND LOWER(TRIM(ud.nom_uni_medi)) = 'mililitro' THEN r.cantidad_reque * 1000.0
                           ELSE r.cantidad_reque
                       END * dp.cant_detalle
                   ) AS total_consumido
            FROM detalles_pedidos_menus dp
            JOIN recetas_menus r ON r.id_menu_fk = dp.id_menu_fk
            JOIN productos p ON p.id_produ_pk = r.id_produ_fk
            JOIN unidades_medidas uo ON uo.id_uni_medi_pk = r.id_uni_medi_fk
            JOIN unidades_medidas ud ON ud.id_uni_medi_pk = p.id_uni_medi_produ_fk
            WHERE dp.id_pedido_fk = NEW.id_pedido_pk
            GROUP BY r.id_produ_fk
        ) consumo ON consumo.id_produ_fk = pr.id_produ_pk
        SET pr.stock_actual_produ = pr.stock_actual_produ - consumo.total_consumido;

        -- Registrar el consumo en consumos_pedidos para auditoría
        INSERT INTO consumos_pedidos (id_pedido_fk, id_produ_fk, cantidad_consumida, id_uni_medi_fk)
        SELECT NEW.id_pedido_pk,
               r.id_produ_fk,
               SUM(
                   CASE 
                       -- gramo -> kilogramo
                       WHEN LOWER(TRIM(uo.nom_uni_medi)) = 'gramo' AND LOWER(TRIM(ud.nom_uni_medi)) = 'kilogramo' THEN r.cantidad_reque * 0.001
                       -- mililitro -> litro
                       WHEN LOWER(TRIM(uo.nom_uni_medi)) = 'mililitro' AND LOWER(TRIM(ud.nom_uni_medi)) = 'litro' THEN r.cantidad_reque * 0.001
                       -- kilogramo -> gramo
                       WHEN LOWER(TRIM(uo.nom_uni_medi)) = 'kilogramo' AND LOWER(TRIM(ud.nom_uni_medi)) = 'gramo' THEN r.cantidad_reque * 1000.0
                       -- litro -> mililitro
                       WHEN LOWER(TRIM(uo.nom_uni_medi)) = 'litro' AND LOWER(TRIM(ud.nom_uni_medi)) = 'mililitro' THEN r.cantidad_reque * 1000.0
                       ELSE r.cantidad_reque
                   END * dp.cant_detalle
               ),
               p.id_uni_medi_produ_fk
        FROM detalles_pedidos_menus dp
        JOIN recetas_menus r ON r.id_menu_fk = dp.id_menu_fk
        JOIN productos p ON p.id_produ_pk = r.id_produ_fk
        JOIN unidades_medidas uo ON uo.id_uni_medi_pk = r.id_uni_medi_fk
        JOIN unidades_medidas ud ON ud.id_uni_medi_pk = p.id_uni_medi_produ_fk
        WHERE dp.id_pedido_fk = NEW.id_pedido_pk
        GROUP BY r.id_produ_fk, p.id_uni_medi_produ_fk;

        -- Marcar productos como 'no disponible' si el stock bajó a 0
        UPDATE productos
        SET estado_produ = 'no disponible'
        WHERE stock_actual_produ <= 0
          AND estado_produ = 'disponible';

        -- Marcar menús como no disponibles si algún ingrediente se agotó
        UPDATE menus m
        SET disponible_menu = 0
        WHERE EXISTS (
            SELECT 1 FROM recetas_menus r
            JOIN productos pr ON pr.id_produ_pk = r.id_produ_fk
            WHERE r.id_menu_fk = m.id_menu_pk
              AND pr.stock_actual_produ <= 0
        );

    END IF;

    -- Devolver stock si el pedido se cancela desde preparando o listo
    IF NEW.estado_pedido = 'cancelado' AND OLD.estado_pedido IN ('preparando', 'listo') THEN

        UPDATE productos pr
        JOIN consumos_pedidos c ON c.id_produ_fk = pr.id_produ_pk
        SET pr.stock_actual_produ = pr.stock_actual_produ + c.cantidad_consumida
        WHERE c.id_pedido_fk = NEW.id_pedido_pk;

        -- Reactivar productos y menús si el stock volvió
        UPDATE productos
        SET estado_produ = 'disponible'
        WHERE stock_actual_produ > 0
          AND estado_produ = 'no disponible';

        UPDATE menus m
        SET disponible_menu = 1
        WHERE NOT EXISTS (
            SELECT 1 FROM recetas_menus r
            JOIN productos pr ON pr.id_produ_pk = r.id_produ_fk
            WHERE r.id_menu_fk = m.id_menu_pk
              AND pr.stock_actual_produ <= 0
        );

    END IF;
END$$

DELIMITER ;