DROP TABLE IF EXISTS monitored_actions;
DROP TYPE IF EXISTS http_method;
CREATE TYPE http_method AS ENUM ('GET', 'POST', 'PUT', 'DELETE');
CREATE TABLE monitored_actions (
	id serial PRIMARY KEY,
	anon_uid varchar(50),
	url_path text,
	http_method http_method,
	get_params text,
	post_params text,
	cookies text,
	timestamp timestamp not null default now()
	);
ALTER TABLE monitored_actions OWNER TO :DJANGO_USER ;
REVOKE ALL ON monitored_actions FROM :DJANGO_USER ;
GRANT INSERT ON monitored_actions TO :DJANGO_USER ;

