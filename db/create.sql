-- 
CREATE TABLE Sermon(
  tcpID VARCHAR(30) NOT NULL PRIMARY KEY, -- EEBO-TCP ID 
  estc VARCHAR(30), -- English Short Title Catalogue ID  
  stc VARCHAR(30), -- Short Title Catalogue ID 
  title TEXT NOT NULL, -- Book title 
  authors TEXT NOT NULL, -- Authors, separated by semi-colons 
  publisher TEXT, -- stationer information 
  pubplace TEXT, -- place of publication 
  subject_headings TEXT, -- LOC subject headings 
  pubyear VARCHAR(30) NOT NULL -- year of publication 
);

CREATE TABLE Segment(
  -- Primary key is the TCP id and segment index 
  tcpID VARCHAR(30) NOT NULL REFERENCES Sermon(tcpID), -- foreign key
  sidx INT NOT NULL, -- index of the segment within a book 
  section INT NOT NULL,-- index of the section within the book 
  loc INT, -- page number or the image reference number on which this segment begins 
  loc_type VARCHAR(30), -- whether location is a page or image
  pidx INT NOT NULL, -- index of the paragraph in which this segment is located  
  tokens TEXT NOT NULL, -- the tokenized segment 
  lemmatized TEXT NOT NULL, -- the lemmata 
  PRIMARY KEY (tcpID, sidx)
);

CREATE TABLE Marginalia(
  -- Primary key is the TCP id, sermon number, segment index and note index 
  tcpID VARCHAR(30) NOT NULL REFERENCES Sermon(tcpID),
  sidx INT NOT NULL, -- segment in which the note is located 
  nidx INT NOT NULL, -- index of the note within the segment  
  tokens TEXT NOT NULL, -- the tokenized segment 
  lemmatized TEXT NOT NULL, -- the lemmata 
  PRIMARY KEY (tcpID, sidx, nidx)
);


CREATE TABLE Citation(
  -- Primary key is the TCP id, segment index, citation index 
  tcpID VARCHAR(30) NOT NULL REFERENCES Sermon(tcpID),
  sidx INT NOT NULL, -- segment in which the citation is located 
  loc TEXT NOT NULL, -- Whether the citation is in the text or margins; if the latter, then indicate 'Note #'
  cidx INT NOT NULL, -- index of the citation within the segment  
  citation TEXT NOT NULL, -- parsed citation
  outlier TEXT, -- parts that cannot be parsed
  replaced TEXT, -- the cleaned tokens that were standardized and parsed  
  PRIMARY KEY (tcpID, sidx, loc, cidx)
);

CREATE TABLE Bible(
  verse_id VARCHAR(500) NOT NULL PRIMARY KEY,
  bible_version VARCHAR(30) NOT NULL, 
  part VARCHAR(500) NOT NULL,
  book VARCHAR(100) NOT NULL,
  chapter INT NOT NULL,
  verse INT NOT NULL,
  verse_text TEXT NOT NULL
);
----------------------------------------------------------------------

CREATE FUNCTION MarginalConstraint() RETURNS TRIGGER AS $$
BEGIN
  IF NOT EXISTS (SELECT tcpID from Segment AS s 
                WHERE s.tcpID = NEW.tcpID 
                AND s.sidx <> NEW.sidx) THEN
    RAISE EXCEPTION 'Cannot insert a non-existing segment';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER MarginalConstraint
  BEFORE INSERT OR UPDATE ON Marginalia
  FOR EACH ROW
  EXECUTE PROCEDURE MarginalConstraint();