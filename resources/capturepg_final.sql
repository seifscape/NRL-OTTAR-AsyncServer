SET timezone = 'UTC';

-- ----------------------------
-- Table structure for `capture_album`
-- ----------------------------
DROP TABLE IF EXISTS capture_album CASCADE;
DROP SEQUENCE IF EXISTS capture_album_seq;

CREATE SEQUENCE capture_album_seq;

CREATE TABLE capture_album (
  capture_id int check (capture_id > 0) NOT NULL DEFAULT NEXTVAL ('capture_album_seq'),
  coordinates varchar(66) NOT NULL,
  annotation text,
  date_created timestamptz NOT NULL,
  date_updated timestamptz,
  PRIMARY KEY (capture_id)
) ;

-- ----------------------------
-- Table structure for `capture_image`
-- ----------------------------
DROP TABLE IF EXISTS capture_image CASCADE;
DROP SEQUENCE IF EXISTS capture_image_seq;

CREATE SEQUENCE capture_image_seq;

CREATE TABLE capture_image (
  image_id int check (image_id > 0) NOT NULL DEFAULT NEXTVAL ('capture_image_seq'),
  encoded TEXT NOT NULL,
  date_created timestamptz NOT NULL,
  PRIMARY KEY (image_id)
) ;

-- ----------------------------
-- Table structure for `capture_image_albums`
-- ----------------------------
DROP TABLE IF EXISTS capture_image_albums;
CREATE TABLE capture_image_albums (
  capture_id int check (capture_id > 0) NOT NULL,
  image_id int check (image_id > 0) NOT NULL,
  PRIMARY KEY (capture_id,image_id),
  CONSTRAINT capture_image_albums_ibfk_1 FOREIGN KEY (capture_id) REFERENCES capture_album (capture_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT capture_image_albums_ibfk_2 FOREIGN KEY (image_id) REFERENCES capture_image (image_id) ON DELETE CASCADE ON UPDATE CASCADE
) ;

DROP INDEX IF EXISTS image_id;
CREATE INDEX image_id ON capture_image_albums (image_id);