from project import app, db
from project.database import game_info, user_info, voted_info, log
import unittest


class TestFunc(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app = app.test_client()
        db.create_all()

        game1 = game_info(game_name="test1_name", game_description="test1_desc", user="test1_user", Tickets=1)
        game2 = game_info(game_name="test2_name", game_description="test2_desc", user="test2_user", Tickets=2)

        db.session.add(game1)
        db.session.add(game2)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # test the index page
    def test_index(self):
        response = self.app.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # test the introduction page
    def test_introduction(self):
        response = self.app.get('/intro', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # test the create new game page
    def test_create_new_game(self):
        response = self.app.get('/New_vote', content_type='html/text')
        self.assertEqual(response.status_code, 302)

    # test delete topics
    def test_delete_topics(self):
        delete1 = game_info.query.filter_by(game_name='test1_name').first()
        delete2 = game_info.query.filter_by(game_name='test2_name').first()
        db.session.delete(delete1)
        db.session.delete(delete2)
        db.session.commit()
        new1 = game_info.query.filter_by(game_name='test1_name').first()
        new2 = game_info.query.filter_by(game_name='test2_name').first()
        self.assertIsNone(new1)
        self.assertIsNone(new2)

    # test is committed
    def test_is_committed(self):
        game3 = game_info(game_name="test3_name", game_description="test3_desc", user="test3_user", Tickets=1)
        game4 = game_info(game_name="test4_name", game_description="test4_desc", user="test4_user", Tickets=1)
        game5 = game_info(game_name="test5_name", game_description="test5_desc", user="test5_user", Tickets=1)
        db.session.add(game3)
        db.session.add(game4)
        db.session.add(game5)
        db.session.commit()
        db.session.flush()

        result3 = game_info.query.filter_by(game_name='test3_name').first()
        result4 = game_info.query.filter_by(game_name='test4_name').first()
        result5 = game_info.query.filter_by(game_name='test5_name').first()

        self.assertIsNotNone(result3)
        self.assertIsNotNone(result4)
        self.assertIsNotNone(result5)

    # test is log out
    def test_is_log_out(self):
        result = self.app.get('/log-out', content_type='html/text')
        self.assertEqual(result.status_code, 302)


if __name__ == '__main__':
    unittest.main()
