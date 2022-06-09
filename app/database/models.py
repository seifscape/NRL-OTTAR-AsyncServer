from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base


# https://stackoverflow.com/a/35787130 asyncio
# https://docs.sqlalchemy.org/en/14/orm/cascades.html#using-foreign-key-on-delete-with-many-to-many-relationships

class CaptureAlbum(Base):
    __tablename__ = 'capture_album'
    capture_id = Column(Integer, primary_key=True)
    annotation = Column(Text, nullable=True)
    coordinates = Column(String(100), nullable=False)
    date_created = Column(DateTime(timezone=True))
    date_updated = Column(DateTime(timezone=True))
    images = relationship('CaptureImage', secondary='capture_image_albums',
                          lazy='subquery', back_populates='image_album', cascade="all, delete")
    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return "<Capture %r>" % self.annotation


class CaptureImage(Base):
    __tablename__ = 'capture_image'
    image_id = Column(Integer, primary_key=True)
    encoded = Column(Text, nullable=False)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    image_album = relationship('CaptureAlbum', back_populates='images',
                               secondary='capture_image_albums', passive_deletes=True)


class CaptureImageAlbums(Base):
    """ A CaptureImageAlbums - middle table between images and albums middle (M:N) """
    __tablename__ = 'capture_image_albums'
    capture_id = Column(Integer, ForeignKey(CaptureAlbum.capture_id), primary_key=True)
    image_id = Column(Integer, ForeignKey(CaptureImage.image_id), primary_key=True)
    ForeignKeyConstraint(('capture_id', 'image_id'),
                         ('capture_album.capture_id', 'capture_image.image_id'),
                         onupdate="CASCADE", ondelete="CASCADE")
