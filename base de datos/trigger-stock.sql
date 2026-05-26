-- =====================================================
-- TRIGGER: descontar stock automáticamente al confirmar pedido
-- Se dispara cuando estado_pedido cambia a 'confirmado'
-- =====================================================

DELIMITER $$

CREATE TRIGGER trg_descontar_stock
AFTER UPDATE ON pedidos
FOR EACH ROW
BEGIN
    IF NEW.estado_pedido = 'confirmado' AND OLD.estado_pedido = 'pendiente' THEN

        -- Descontar stock de cada producto usado en el pedido
        UPDATE productos pr
        JOIN (
            SELECT r.id_produ_fk,
                   SUM(r.cantidad_requerida * dp.cant_detalle) AS total_consumido
            FROM detalles_pedidos_menus dp
            JOIN recetas_menus r ON r.id_menu_fk = dp.id_menu_fk
            WHERE dp.id_pedido_fk = NEW.id_pedido_pk
            GROUP BY r.id_produ_fk
        ) consumo ON consumo.id_produ_fk = pr.id_produ_pk
        SET pr.stock_actual_produ = pr.stock_actual_produ - consumo.total_consumido;

        -- Registrar el consumo en consumos_pedidos para auditoría
        INSERT INTO consumos_pedidos (id_pedido_fk, id_produ_fk, cantidad_consumida, id_uni_medi_fk)
        SELECT NEW.id_pedido_pk,
               r.id_produ_fk,
               SUM(r.cantidad_requerida * dp.cant_detalle),
               r.id_uni_medi_fk
        FROM detalles_pedidos_menus dp
        JOIN recetas_menus r ON r.id_menu_fk = dp.id_menu_fk
        WHERE dp.id_pedido_fk = NEW.id_pedido_pk
        GROUP BY r.id_produ_fk, r.id_uni_medi_fk;

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

    -- Devolver stock si el pedido se cancela
    IF NEW.estado_pedido = 'cancelado' AND OLD.estado_pedido IN ('confirmado', 'preparando') THEN

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