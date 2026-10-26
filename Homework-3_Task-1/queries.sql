SELECT *
FROM tasks
WHERE user_id = 1;


SELECT *
FROM tasks
WHERE status_id = (
    SELECT id
    FROM status
    WHERE name = 'new'
);


UPDATE tasks
SET status_id = (
    SELECT id
    FROM status
    WHERE name = 'in progress'
)
WHERE id = 1;


SELECT *
FROM users
WHERE id NOT IN (
    SELECT user_id
    FROM tasks
);


INSERT INTO tasks (
    title,
    description,
    status_id,
    user_id
)
VALUES (
    'New task',
    'Task description',
    (
        SELECT id
        FROM status
        WHERE name = 'new'
    ),
    1
);


SELECT *
FROM tasks
WHERE status_id <> (
    SELECT id
    FROM status
    WHERE name = 'completed'
);


DELETE FROM tasks
WHERE id = 1;


SELECT *
FROM users
WHERE email LIKE '%@example.com';


UPDATE users
SET fullname = 'Updated User Name'
WHERE id = 1;


SELECT
    status.name,
    COUNT(tasks.id) AS task_count
FROM status
LEFT JOIN tasks
    ON tasks.status_id = status.id
GROUP BY
    status.id,
    status.name
ORDER BY status.id;


SELECT tasks.*
FROM tasks
JOIN users
    ON tasks.user_id = users.id
WHERE users.email LIKE '%@example.com';


SELECT *
FROM tasks
WHERE description IS NULL
   OR TRIM(description) = '';


SELECT
    users.id,
    users.fullname,
    users.email,
    tasks.id AS task_id,
    tasks.title,
    tasks.description
FROM users
INNER JOIN tasks
    ON users.id = tasks.user_id
INNER JOIN status
    ON tasks.status_id = status.id
WHERE status.name = 'in progress';


SELECT
    users.id,
    users.fullname,
    users.email,
    COUNT(tasks.id) AS task_count
FROM users
LEFT JOIN tasks
    ON users.id = tasks.user_id
GROUP BY
    users.id,
    users.fullname,
    users.email
ORDER BY users.id;