-- =====================================================
-- STORED PROCEDURE: verificar si hay stock para un pedido
-- Django lo llama antes de confirmar el pedido
-- =====================================================

DELIMITER $$

CREATE PROCEDURE verificar_stock_pedido(
    IN p_id_pedido INT,
    OUT p_tiene_stock TINYINT,
    OUT p_mensaje VARCHAR(500)
)
BEGIN
    DECLARE v_faltante VARCHAR(500) DEFAULT '';
    DECLARE v_count INT DEFAULT 0;

    -- Busca productos con stock insuficiente para este pedido
    SELECT COUNT(*), GROUP_CONCAT(
        CONCAT(pr.nom_produ, ' (necesita: ', SUM(r.cantidad_requerida * dp.cant_detalle),
               ' ', um.abreviatura, ', hay: ', pr.stock_actual_produ, ')')
        SEPARATOR ' | '
    )
    INTO v_count, v_faltante
    FROM detalles_pedidos_menus dp
    JOIN recetas_menus r         ON r.id_menu_fk  = dp.id_menu_fk
    JOIN productos pr            ON pr.id_produ_pk = r.id_produ_fk
    JOIN unidades_medidas um     ON um.id_uni_medi_pk = r.id_uni_medi_fk
    WHERE dp.id_pedido_fk = p_id_pedido
    GROUP BY pr.id_produ_pk
    HAVING SUM(r.cantidad_requerida * dp.cant_detalle) > pr.stock_actual_produ;

    IF v_count = 0 THEN
        SET p_tiene_stock = 1;
        SET p_mensaje = 'Stock suficiente';
    ELSE
        SET p_tiene_stock = 0;
        SET p_mensaje = CONCAT('Stock insuficiente: ', v_faltante);
    END IF;
END$$

DELIMITER ;
