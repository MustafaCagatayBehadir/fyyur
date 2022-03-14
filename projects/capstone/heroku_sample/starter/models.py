import os
from sqlalchemy import Column, String, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
import enum

database_path = os.environ['DATABASE_URL']
if database_path.startswith("postgres://"):
    database_path = database_path.replace("postgres://", "postgresql://", 1)

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


class NodeType(str, enum.Enum):
    standalone = "standalone"
    vpc = "vpc"


class NodeRole(str, enum.Enum):
    access_leaf = "access-leaf"
    border_leaf = "border-leaf"
    spine = "spine"


'''
Node
Have id, fabric, hostname, type, role and vpc-id if node type is VPC
'''


class Node(db.Model):
    __tablename__ = 'nodes'

    id = Column(Integer, primary_key=True)
    fabric = Column(String)
    hostname = Column(String)
    role = Column(Enum(NodeRole), nullable=False)
    type = Column(Enum(NodeType))
    vpc_id = Column(Integer, ForeignKey('nodegroups.id'))

    def __init__(self, fabric, hostname, role, type, vpc_id):
        self.fabric = fabric
        self.hostname = hostname
        self.role = role
        self.type = type
        self.vpc_id = vpc_id

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        if self.vpc_id:
            return {
                'id': self.id,
                'fabric': self.fabric,
                'hostname': self.hostname,
                'role': self.role,
                'type': self.type,
                'vpc-id': self.vpc_id
            }
        else:
            return {
                'id': self.id,
                'fabric': self.fabric,
                'hostname': self.hostname,
                'role': self.role,
                'type': self.type
            }


class NodeGroup(db.Model):
    __tablename__ = 'nodegroups'

    id = Column(db.Integer, primary_key=True)
    fabric = Column(String)
    node_1 = Column(String)
    node_2 = Column(String)
    node = relationship("Node", backref="nodegroup", lazy=True)

    def __init__(self, fabric, node_1, node_2):
        self.fabric = fabric
        self.node_1 = node_1
        self.node_2 = node_2

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'fabric': self.fabric,
            'node-1': self.node_1,
            'node-2': self.node_2
        }