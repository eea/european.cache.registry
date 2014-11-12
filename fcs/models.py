# coding: utf-8
from sqlalchemy import (
    Column, DateTime, Float, ForeignKey, Integer, LargeBinary, SmallInteger,
    String, Table, Text, Boolean
)
from sqlalchemy.orm import relationship
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager


db = SQLAlchemy()
Base = db.Model

db_manager = Manager()


@db_manager.command
def init():
    return db.create_all()

