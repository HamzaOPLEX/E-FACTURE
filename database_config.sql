SET collation_connection = 'utf8_general_ci';
ALTER DATABASE NTFMDB_CLIENT_NAME CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE dashboard_app_clients CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE dashboard_app_products CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE dashboard_app_devis_items CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE dashboard_app_bl_items CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE dashboard_app_facture_items CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE dashboard_app_warnning CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE dashboard_app_history CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
