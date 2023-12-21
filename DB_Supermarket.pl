% productos en promoción "promotion(<nombre_producto>, <marca>, <categoria>, <precio>, <cantidad (gr/ml)>, <unidades a llevar>).".

% Lacteos
promotion(leche, la_serenisima, lacteos, 378, '1L', 3).
promotion(queso, sancor, lacteos, 1790, '1kg', 1).
promotion(yogur, danone, lacteos, 90, '150ml', 6).
promotion(tapa_pascualina, la_saltenia, lacteos, 308, '400g', 2).
promotion(crema_batida, la_serenisima, lacteos, 623, '520ml', 2).
promotion(manteca, danica, lacteos, 500, '100g', 2).

% Carniceria
promotion(tapa_de_nalga, la_estancia, carniceria, 2989, '1kg', 1).
promotion(vacio_novillito, criollo, carniceria, 3339, '1kg', 1).
promotion(roast_beef, parrillero, carniceria, 2669, '1kg', 1).
promotion(peceto_novillito, la_estancia, carniceria, 4099, '1kg', 1).
promotion(asado_novillito, criollo, carniceria, 2689, '1kg', 1).

% Verduleria
promotion(papa, chola, verduleria, 679, '1kg', 1).
promotion(zanahoria, del_campo, verduleria, 299, '1kg', 1).
promotion(lechuga, freskale, verduleria, 459, '1kg', 1).
promotion(cebolla, del_campo, verduleria, 299, '1kg', 1).
promotion(tomate, fuji, verduleria, 999, '1kg', 1).
promotion(ajo, del_campo, verduleria, 2590, '1kg', 1).
promotion(zapallo_anco, fuji, verduleria, 179, '1kg', 1).

% Galletitas
promotion(pepas, trio, galletitas, 377, '300g', 3).
promotion(oreo_chocolate, oreo, galletitas, 930, '118g', 3).
promotion(okebon_leche, okebon, galletitas, 210, '150g', 3).
promotion(frutigram_chocolate, frutigram, galletitas, 475, '500g', 3).
promotion(lincoln, terrabusi, galletitas, 356, '219g', 3).
promotion(bizcochos, nueve_de_oro, galletitas, 226, '215g', 3).
promotion(oblea, opera, galletitas, 107, '55g', 3).
promotion(surtido, bagley, galletitas, 488, '398g', 3).

% Limpieza
promotion(jabon_liquido, ala, limpieza, 1406, '750ml', 2).
promotion(detergente, magistral, limpieza, 1059, '750ml', 2).
promotion(lavandina, ayudin, limpieza, 537, '2l', 2).
promotion(papel_higienico, higienol, limpieza, 644, '4 rollos', 2).
promotion(trapo_pisos, essencial, limpieza, 509, '1 unidad', 1).
promotion(limpiavidrios, procenex, limpieza, 260, '820ml',1).

% Bebidas
promotion(cola, coca_cola, bebidas, 715, '2.25l', 3).
promotion(jugo, bc, bebidas, 40, '4g', 6).
promotion(cerveza_rubia, andes, bebidas, 2200, '473ml', 6).
promotion(agua_mineral, epura, bebidas, 180, '2l', 3).
promotion(vino_tinto, malbec, bebidas, 1499, '750ml', 1).
promotion(energizante, monster, bebidas, 399, '473ml', 3).

% Panaderia
promotion(pan_blanco, bimbo, panaderia, 799, '550g', 3).
promotion(medialunas, mariposa, panaderia, 1440, '1 docena', 1).
promotion(baguette, la_parisienne, panaderia, 278, '300g', 2).
promotion(madalenas, bon, panaderia, 580, '1kg', 1).
promotion(donut, delicias, panaderia, 199, '100g', 4).
promotion(prepizza, mariposa, panaderia, 299, '575g', 3).

% Reposteria
promotion(premezcla, exquisita, reposteria, 387, '540g', 3).
promotion(esencia_vainilla, alicante, reposteria, 230, '100ml', 2).
promotion(gelatina, exquisita, reposteria, 137, '40g', 3).
promotion(flan, exquisita, reposteria, 136, '25g', 3).
promotion(bicarbonato, alicante, reposteria, 120, '50g', 2).


% Reglas: obtener promociones por categoría
% get_promotions(Category, Promotions) :-
%    findall(Promo, promotion(Promo, Category, _, _), Promotions).

% Regla para obtener promociones por categoría
get_promotions_by_category(Category, Promotions) :-
    findall((Nombre, Marca, Precio, Cantidad, Unidades), promotion(Nombre, Marca, Category, Precio, Cantidad, Unidades), Promotions).

% Regla para obtener promociones con precio menor o igual al valor dado
get_promotions_below_price(Price, Promotions) :-
    findall(
        (Nombre, Marca, Categoria, Precio, Cantidad, Unidades),
        (promotion(Nombre, Marca, Categoria, Precio, Cantidad, Unidades), Precio =< Price),
        Promotions
    ).
