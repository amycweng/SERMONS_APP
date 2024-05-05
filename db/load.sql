\COPY Sermon FROM 'sermons.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Sermon FROM 'sermons_missing.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Author FROM 'authors.csv' WITH DELIMITER ',' NULL '' CSV

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

\COPY Citation FROM 'pre-Elizabethan/citations.csv' WITH DELIMITER ',' NULL '' CSV

\COPY Bible FROM 'kjv.csv' WITH DELIMITER ',' NULL '' CSV
\COPY BiblePhrase FROM 'bible_phrases.csv' WITH DELIMITER ',' NULL '' CSV
\COPY BiblePhraseLabel FROM 'bible_phrase_indices.csv' WITH DELIMITER ',' NULL '' CSV

\COPY PossibleQuoteParaphrase FROM 'possible_quotes_paraphrases.csv' WITH DELIMITER ',' NULL '' CSV
