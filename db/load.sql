\COPY Sermon FROM 'sermons.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Sermon FROM 'sermons_missing.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Author FROM 'authors.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Pubplace FROM 'pubplace.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Section FROM 'sections.csv' WITH DELIMITER ',' NULL '' CSV
\COPY SubjectHeading FROM 'subjects.csv' WITH DELIMITER ',' NULL '' CSV

\COPY Bible FROM 'Bibles/KJV.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Bible FROM 'Bibles/Geneva.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Bible FROM 'Bibles/Douay-Rheims.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Bible FROM 'Bibles/Tyndale.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Bible FROM 'Bibles/Vulgate.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Bible FROM 'Bibles/Wycliffe.csv' WITH DELIMITER ',' NULL '' CSV

\COPY QuoteParaphrase FROM 'paraphrases/sample.csv' WITH DELIMITER ',' NULL '' CSV