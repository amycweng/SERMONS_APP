\COPY Sermon FROM 'sermons.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Sermon FROM 'sermons_missing.csv' WITH DELIMITER ',' NULL '' CSV

\COPY Segment FROM 'pre-Elizabethan/A0_body.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Segment FROM 'pre-Elizabethan/A1_body.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Segment FROM 'pre-Elizabethan/A2_body.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Segment FROM 'pre-Elizabethan/A6_body.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Segment FROM 'pre-Elizabethan/A7_body.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Segment FROM 'pre-Elizabethan/B_body.csv' WITH DELIMITER ',' NULL '' CSV

\COPY Marginalia FROM 'pre-Elizabethan/A0_margin.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Marginalia FROM 'pre-Elizabethan/A1_margin.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Marginalia FROM 'pre-Elizabethan/A2_margin.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Marginalia FROM 'pre-Elizabethan/A6_margin.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Marginalia FROM 'pre-Elizabethan/A7_margin.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Marginalia FROM 'pre-Elizabethan/B_margin.csv' WITH DELIMITER ',' NULL '' CSV

\COPY InTextCitation FROM 'pre-Elizabethan/citations_body.csv' WITH DELIMITER ',' NULL '' CSV
\COPY MarginalCitation FROM 'pre-Elizabethan/citations_margin.csv' WITH DELIMITER ',' NULL '' CSV
