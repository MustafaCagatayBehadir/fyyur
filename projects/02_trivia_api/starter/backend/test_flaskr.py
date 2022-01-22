import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'postgres', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['categories']))
        self.assertIn(data['current_category'], ('Science', 'Art', 'Geography', 'History', 'Entertainment', 'Sports'))
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
        self.assertEqual(data['error'], 404)

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(data['categories'], dict)
        self.assertTrue(data['categories'])

    def test_delete_question(self):
         res = self.client().delete('/questions/2')
         data = json.loads(res.data)

         self.assertEqual(res.status_code, 200)
         self.assertIsInstance(data['questions'], list)
         self.assertEqual(data['success'], True)
         self.assertTrue(data['total_questions'])

    def test_404_if_question_does_not_exist(self):
         res = self.client().delete('/questions/1000')
         data = json.loads(res.data)

         self.assertEqual(res.status_code, 404)
         self.assertEqual(data['success'], False)
         self.assertEqual(data['message'], 'resource not found')
         self.assertEqual(data['error'], 404)           



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main(verbosity=2)