SELECT 'CREATE DATABASE dailyoracle'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'dailyoracle')\gexec