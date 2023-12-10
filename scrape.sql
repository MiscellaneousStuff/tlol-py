SELECT
	game_id
FROM
	players
WHERE
	team = 100 AND
	time_spent_dead < 25 AND
	seconds > 300;