const apiKey = '2bca2b98eb9f47b486bd02d72febbf9b';

const SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:admin@localhost:5432/whats_for_dinner';
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:admin@localhost:5432/whats_for_dinner').replace('postgres://', 'postgresql://')

export {apiKey};