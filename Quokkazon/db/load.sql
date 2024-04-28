\COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
-- since id is auto-generated; we need the next command to adjust the counter
-- for auto-generation so next INSERT will not clash with ids loaded above:
SELECT pg_catalog.setval('public.users_id_seq',
                         (SELECT MAX(id)+1 FROM Users),
                         false);

\COPY Seller FROM 'Sellers.csv' WITH DELIMITER ',' NULL '' CSV

\COPY Category FROM 'Category.csv' WITH DELIMITER ',' NULL '' CSV
-- SELECT pg_catalog.setval('public.category_id_seq',
--                          (SELECT MAX(id)+1 FROM Category),
--                          false);

\COPY Products FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV
-- SELECT pg_catalog.setval('public.products_id_seq',
--                          (SELECT MAX(id)+1 FROM Products),
--                          false);

\COPY Purchases FROM 'Purchases.csv' WITH DELIMITER ',' NULL '' CSV

\COPY SellerFeedback FROM 'SellerFeedback.csv' WITH DELIMITER ',' NULL '' CSV


\COPY ProductFeedback FROM 'ProductFeedback.csv' WITH DELIMITER ',' NULL '' CSV

\COPY UpvoteProductReview FROM 'ProductReviewUpvotes.csv' WITH DELIMITER ',' NULL '' CSV

\COPY UpvoteSellerReview FROM 'SellerReviewUpvotes.csv' WITH DELIMITER ',' NULL '' CSV

\COPY Messages FROM 'Messages.csv' WITH DELIMITER ',' NULL '' CSV

\COPY Inventory FROM 'Inventory.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Cart FROM 'Cart.csv' WITH DELIMITER ',' NULL '' CSV
