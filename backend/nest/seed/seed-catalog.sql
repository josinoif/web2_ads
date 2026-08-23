-- Seed parcial: só catálogo (após cap. 5 — tabela products).
-- Use seed.sql completo depois de auth (users) + pedidos (orders).

DELETE FROM products;

INSERT INTO products (name, price, stock) VALUES
  ('Caneca Nest', 39.90, 10),
  ('Camiseta ADS', 59.90, 25);

SELECT id, name, price, stock FROM products ORDER BY id;
