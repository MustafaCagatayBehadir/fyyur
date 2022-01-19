#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from os import name
from re import VERBOSE
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form, csrf
from sqlalchemy.orm import backref
from werkzeug.wrappers import response
from forms import *
from datetime import datetime
from models import db, Venue, Artist, Show
import config
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db.init_app(app)

migrate = Migrate(app, db, compare_type=True)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = list()
    places = set((venue.city, venue.state) for venue in Venue.query.all())
    for city, state in places:
        data.append({
            "city": city,
            "state": state,
            "venues": [{
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len([show for show in venue.shows if show.start_time > datetime.now()])
            } for venue in Venue.query.all() if venue.city == city and venue.state == state]
        })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
<<<<<<< HEAD
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
=======
    search_term = request.form.get('search_term')
    response = {
        "count": len(Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()),
        "data": [{
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len([show for show in venue.shows if show.start_time > datetime.now()])
        } for venue in Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()]
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

>>>>>>> 53a745655f240530e90381c74ec73db7c01909b3

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "image_link": venue.image_link,
        "past_shows": [{
            "artist_id": show.artist_id,
            "artist_name": Artist.query.get(show.artist_id).name,
            "artist_image_link": Artist.query.get(show.artist_id).image_link,
            "start_time": str(show.start_time)
        } for show in venue.past_shows()],
        "upcoming_shows": [{
            "artist_id": show.artist_id,
            "artist_name": Artist.query.get(show.artist_id).name,
            "artist_image_link": Artist.query.get(show.artist_id).image_link,
            "start_time": str(show.start_time)
        } for show in venue.upcoming_shows()],
        "past_shows_count": len(venue.past_shows()),
        "upcoming_shows_count": len(venue.upcoming_shows())
    }
    if data.get('seeking_talent'):
        data['seeking_description'] = venue.seeking_description
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        error = False
        try:
            _name = request.form.get('name')
            _city = request.form.get('city')
            _state = request.form.get('state')
            _address = request.form.get('address')
            _phone = request.form.get('phone')
            _genres = request.form.getlist('genres')
            _facebook_link = request.form.get('facebook_link')
            _image_link = request.form.get('image_link')
            _website_link = request.form.get('website_link')
            _seeking_talent = True if request.form.get(
                'seeking_talent') else False
            _seeking_description = request.form['seeking_description'] if request.form.get(
                'seeking_description') else ''
            venue = Venue(name=_name, city=_city, state=_state, address=_address, phone=_phone, genres=_genres, facebook_link=_facebook_link,
                          image_link=_image_link, website_link=_website_link, seeking_talent=_seeking_talent, seeking_description=_seeking_description)
            db.session.add(venue)
            db.session.commit()
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')
        except:
            db.session.rollback()
            flash('An error occurred. Venue ' +
                  request.form['name'] + ' could not be listed.')
            error = True
            print(sys.exc_info())
        finally:
            db.session.close()
        if error:
            abort(500)
        else:
            return render_template('pages/home.html')
    else:
        flash(form.errors)
        return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
    error = False
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('Venue ' + venue.name + ' was successfully deleted!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' +
              venue.name + ' could not be deleted.')
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    data = [{
        "id": artist.id,
        "name": artist.name
    } for artist in Artist.query.all()]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term')
    response = {
        "count": len(Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()),
        "data": [{
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len([show for show in artist.shows if show.start_time > datetime.now()])
        } for artist in Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()]
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "seeking_venue": artist.seeking_venue,
        "image_link": artist.image_link,
        "past_shows": [{
            "venue_id": show.venue_id,
            "venue_name": Venue.query.get(show.venue_id).name,
            "venue_image_link": Venue.query.get(show.venue_id).image_link,
            "start_time": str(show.start_time)
        } for show in artist.past_shows()],
        "upcoming_shows": [{
            "venue_id": show.venue_id,
            "venue_name": Venue.query.get(show.venue_id).name,
            "venue_image_link": Venue.query.get(show.venue_id).image_link,
            "start_time": str(show.start_time)
        } for show in artist.upcoming_shows()],
        "past_shows_count": len(artist.past_shows()),
        "upcoming_shows_count": len(artist.upcoming_shows()),
    }
    if artist.website_link:
        data['website'] = artist.website_link
    if artist.facebook_link:
        data['facebook_link'] = artist.facebook_link
    if data['seeking_venue']:
        data['seeking_description'] = artist.seeking_description
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False
    try:
        artist = Artist.query.get(artist_id)
        artist.name = request.form.get('name')
        artist.city = request.form.get('city')
        artist.state = request.form.get('state')
        artist.phone = request.form.get('phone')
        artist.genres = request.form.getlist('genres')
        artist.facebook_link = request.form.get('facebook_link')
        artist.image_link = request.form.get('image_link')
        artist.website_link = request.form.get('website_link')
        artist.seeking_venue = True if request.form.get(
            'seeking_talent') else False
        artist.seeking_description = request.form['seeking_description'] if request.form.get(
            'seeking_description') else ''
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully edited!')
    except:
        db.session.rollback()
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be edited.')
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    try:
        venue = Venue.query.get(venue_id)
        venue.name = request.form.get('name')
        venue.city = request.form.get('city')
        venue.state = request.form.get('state')
        venue.address = request.form.get('address')
        venue.phone = request.form.get('phone')
        venue.genres = request.form.getlist('genres')
        venue.facebook_link = request.form.get('facebook_link')
        venue.image_link = request.form.get('image_link')
        venue.website_link = request.form.get('website_link')
        venue.seeking_talent = True if request.form.get(
            'seeking_talent') else False
        venue.seeking_description = request.form['seeking_description'] if request.form.get(
            'seeking_description') else ''
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully edited!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be edited.')
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        error = False
        try:
            _name = request.form.get('name')
            _city = request.form.get('city')
            _state = request.form.get('state')
            _phone = request.form.get('phone')
            _genres = request.form.getlist('genres')
            _facebook_link = request.form.get('facebook_link')
            _image_link = request.form.get('image_link')
            _website_link = request.form.get('website_link')
            _seeking_venue = True if request.form.get('seeking_talent') else False
            _seeking_description = request.form['seeking_description'] if request.form.get(
                'seeking_description') else ''
            artist = Artist(name=_name, city=_city, state=_state, phone=_phone, image_link=_image_link, genres=_genres,
                            facebook_link=_facebook_link, website_link=_website_link, seeking_venue=_seeking_venue, seeking_description=_seeking_description)
            db.session.add(artist)
            db.session.commit()
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
        except:
            db.session.rollback()
            flash('An error occurred. Artist ' +
                request.form['name'] + ' could not be listed.')
            error = True
            print(sys.exc_info())
        finally:
            db.session.close()
        if error:
            abort(500)
        else:
            return render_template('pages/home.html')
    else:
        flash(form.errors)
        return render_template('pages/home.html')        


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    data = [{
        "venue_id": show.venue_id,
        "venue_name": Venue.query.get(show.venue_id).name,
        "artist_id": show.artist_id,
        "artist_name": Artist.query.get(show.artist_id).name,
        "artist_image_link": Artist.query.get(show.artist_id).image_link,
        "start_time": str(show.start_time)
    } for show in Show.query.all()]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        error = False
        try:
            _artist_id = request.form.get('artist_id')
            _venue_id = request.form.get('venue_id')
            _start_time = request.form.get('start_time')
            show = Show(artist_id=_artist_id, venue_id=_venue_id,
                        start_time=_start_time)
            db.session.add(show)
            db.session.commit()
            flash('Show was successfully listed!')
        except Exception as e:
            print(e)
            db.session.rollback()
            flash('An error occurred. Show could not be listed.')
            error = True
        finally:
            db.session.close()
        if error:
            abort(500)
        else:
            return render_template('pages/home.html')
    else:
        flash(form.errors)
        return render_template('pages/home.html')        


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
