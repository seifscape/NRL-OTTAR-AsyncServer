from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base


class CaptureAlbum(Base):
    __tablename__ = 'capture_album'
    album_id = Column(Integer, primary_key=True)
    annotation = Column(Text, nullable=True)
    coordinates = Column(String(100), nullable=False)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    date_updated = Column(DateTime(timezone=True), server_default=func.now())
    # images = relationship('CaptureImage', secondary='capture_image_albums')
    # https://stackoverflow.com/a/35787130
    images = relationship('CaptureImage', secondary='capture_image_albums', lazy='subquery')
    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return "<Capture %r>" % self.annotation


class CaptureImage(Base):
    __tablename__ = 'capture_image'
    image_id = Column(Integer, primary_key=True)
    encoded = Column(Text, nullable=False)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    # albums = db.relationship('CaptureAlbum', secondary='capture_image_albums')


class CaptureImageAlbums(Base):
    """ middle table M:N """
    __tablename__ = 'capture_image_albums'
    album_id = Column(Integer, ForeignKey(CaptureAlbum.album_id), primary_key=True)
    image_id = Column(Integer, ForeignKey(CaptureImage.image_id), primary_key=True)
    ForeignKeyConstraint(
        ('album_id', 'image_id'),
        ('capture_album.album_id', 'capture_image.image_id'),
        onupdate="CASCADE", ondelete="CASCADE")
