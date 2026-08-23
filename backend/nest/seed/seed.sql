-- Seed oficial completo da trilha loja-api (linha P)
-- Senha: secret123  |  ana=ADMIN  |  cli=CLIENT
-- Pré-requisito: tabelas users, products, orders e order_items
--   já criadas pela API (synchronize) — tipicamente a partir do cap. 6.
-- Antes de auth/pedidos, use seed-catalog.sql.

DELETE FROM order_items;
DELETE FROM orders;
DELETE FROM products;
DELETE FROM users;

INSERT INTO users (username, email, password, role) VALUES
  ('ana', 'ana@loja.test', '$2b$10$2gYSaz98rFtxXgbjMktX..g1WvfCU3fZ8YrQVyK3rUYNCBzSfM2x2', 'ADMIN'),
  ('cli', 'cli@loja.test', '$2b$10$2gYSaz98rFtxXgbjMktX..g1WvfCU3fZ8YrQVyK3rUYNCBzSfM2x2', 'CLIENT');

INSERT INTO products (name, price, stock) VALUES
  ('Caneca Nest', 39.90, 10),
  ('Camiseta ADS', 59.90, 25);

SELECT id, username, role FROM users ORDER BY id;
SELECT id, name, price, stock FROM products ORDER BY id;
