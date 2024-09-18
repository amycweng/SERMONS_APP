\COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Sermon FROM 'sermons.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Sermon FROM 'sermons_missing.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Author FROM 'authors.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Pubplace FROM 'pubplace.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Section FROM 'sections.csv' WITH DELIMITER ',' NULL '' CSV
\COPY SubjectHeading FROM 'subjects.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Topics FROM 'topics.csv' WITH DELIMITER ',' NULL '' CSV
\COPY TopicWords FROM 'topic_words.csv' WITH DELIMITER ',' NULL '' CSV

\COPY Bible FROM 'Bibles/KJV.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Bible FROM 'Bibles/Geneva.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Bible FROM 'Bibles/Douay-Rheims.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Bible FROM 'Bibles/Tyndale.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Bible FROM 'Bibles/Vulgate.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Bible FROM 'Bibles/Wycliffe.csv' WITH DELIMITER ',' NULL '' CSV

\COPY Citation FROM 'corrected_citations.csv'  WITH DELIMITER ',' NULL '' CSV

-- \COPY ChromaIndices FROM 'chroma_indices/INFO_CivilWar_margin.csv' WITH DELIMITER ',' NULL '' CSV
-- \COPY ChromaIndices FROM 'chroma_indices/INFO_CivilWar.csv' WITH DELIMITER ',' NULL '' CSV
