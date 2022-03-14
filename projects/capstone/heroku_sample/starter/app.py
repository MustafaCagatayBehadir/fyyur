from flask import Flask, request, jsonify, abort
from models import setup_db, db, Node, NodeGroup
from auth import requires_auth, AuthError
from flask_cors import CORS
import sys


def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.route('/nodes')
    @requires_auth(permission='get:nodes')
    def get_nodes(payload):
        try:
            nodes = Node.query.order_by(Node.id).all()
            return jsonify({
                'nodes': [node.format() for node in nodes],
                'total_nodes': len(Node.query.all())
            })
        except:
            print(sys.exc_info())
            abort(422)

    @app.route('/nodes', methods=['POST'])
    @requires_auth(permission='post:nodes')
    def create_nodes(payload):
        try:
            body = request.get_json()
            node = Node(fabric=body['fabric'], hostname=body['hostname'],
                        role=body['role'], type=body['type'], vpc_id=body['vpc-id'])
            node.insert()
            return jsonify({
                "success": True,
                "created": node.id,
                "nodes": [node.format() for node in Node.query.order_by(Node.id).all()],
                "total_nodes": len(Node.query.all())
            }), 201
        except Exception as e:
            print(e)
            db.session.rollback()
            print(sys.exc_info())
            abort(422)
        finally:
            db.session.close()

    @app.route('/nodes/<int:node_id>', methods=['PATCH'])
    @requires_auth(permission='patch:nodes')
    def update_node(payload, node_id):
        _error_code = None
        try:
            body = request.get_json()
            node = Node.query.filter(Node.id == node_id).one_or_none()
            if node is None:
                _error_code = 404
                abort(404)
            node.vpc_id = body['vpc-id']
            node.update()
            return jsonify({
                "success": True,
                "node": [node.format()],
            })
        except Exception as e:
            print(e)
            db.session.rollback()
            print(sys.exc_info())
            _error_code = 422 if _error_code is None else _error_code
            abort(_error_code)
        finally:
            db.session.close()

    @app.route('/nodes/<int:node_id>', methods=['DELETE'])
    @requires_auth(permission='delete:nodes')
    def delete_node(payload, node_id):
        _error_code = None
        try:
            node = Node.query.filter(Node.id == node_id).one_or_none()
            if node is None:
                _error_code = 404
                abort(404)
            node.delete()
            return jsonify({
                "success": True,
                "deleted": node_id,
                "nodes": [node.format() for node in Node.query.order_by(Node.id).all()],
                "total_nodes": len(Node.query.all())
            })
        except Exception as e:
            print(e)
            db.session.rollback()
            print(sys.exc_info())
            _error_code = 422 if _error_code is None else _error_code
            abort(_error_code)
        finally:
            db.session.close()

    @app.route('/nodegroups')
    @requires_auth(permission='get:nodegroups')
    def get_nodegroups(payload):
        try:
            nodegroups = NodeGroup.query.order_by(NodeGroup.id).all()
            return jsonify({
                'nodegroups': [nodegroup.format() for nodegroup in nodegroups],
                'total_nodegroups': len(NodeGroup.query.all())
            })
        except:
            print(sys.exc_info())
            abort(422)

    @app.route('/nodegroups', methods=['POST'])
    @requires_auth(permission='post:nodegroups')
    def create_nodegroup(payload):
        try:
            body = request.get_json()
            nodegroup = NodeGroup(
                fabric=body['fabric'], node_1=body['node-1'], node_2=body['node-2'])
            nodegroup.insert()
            return jsonify({
                "success": True,
                "created": nodegroup.id,
                "nodegroups": [nodegroup.format() for nodegroup in NodeGroup.query.order_by(NodeGroup.id).all()],
                "total_nodegroups": len(NodeGroup.query.all())
            }), 201
        except Exception as e:
            print(e)
            db.session.rollback()
            print(sys.exc_info())
            abort(422)
        finally:
            db.session.close()

    @app.route('/nodegroups/<int:nodegroup_id>', methods=['DELETE'])
    @requires_auth(permission='delete:nodegroups')
    def delete_nodegroup(payload, nodegroup_id):
        _error_code = None
        try:
            nodegroup = NodeGroup.query.filter(
                NodeGroup.id == nodegroup_id).one_or_none()
            if nodegroup is None:
                _error_code = 404
                abort(404)
            nodegroup.delete()
            return jsonify({
                "success": True,
                "deleted": nodegroup_id,
                "nodes": [nodegroup.format() for nodegroup in NodeGroup.query.order_by(NodeGroup.id).all()],
                "total_nodes": len(Node.query.all())
            })
        except Exception as e:
            print(e)
            db.session.rollback()
            print(sys.exc_info())
            _error_code = 422 if _error_code is None else _error_code
            abort(_error_code)
        finally:
            db.session.close()

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    @app.errorhandler(AuthError)
    def authentication_failed(autherror):
        return jsonify({
            "success": False,
            "error": autherror.status_code,
            "message": autherror.error["description"]
        }), autherror.status_code

    return app


app = create_app()

if __name__ == '__main__':
    app.run()
