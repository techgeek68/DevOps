<?php
session_start();
$_SESSION['visits'] = ($_SESSION['visits'] ?? 0) + 1;
$name = htmlspecialchars($_POST['name'] ?? '');
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PHP Demo</title>
    <style>
        body {
            font-family: sans-serif;
            max-width: 700px;
            margin: 3rem auto;
            padding: 20px;
            color: #333;
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 1rem;
        }
        p {
            margin: 0.4rem 0;
        }
        form {
            margin-top: 1.2rem;
        }
        input[type="text"] {
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 1rem;
        }
        button {
            padding: 8px 16px;
            margin-left: 6px;
            border: 1px solid #2c3e50;
            background: #2c3e50;
            color: #fff;
            border-radius: 4px;
            font-size: 1rem;
            cursor: pointer;
        }
        button:hover {
            background: #1f2d3a;
        }
    </style>
</head>
<body>
    <h1>PHP FPM Demo</h1>
    <p><strong>Server:</strong> <?= htmlspecialchars($_SERVER['SERVER_NAME']) ?></p>
    <p><strong>PHP Version:</strong> <?= PHP_VERSION ?></p>
    <p><strong>Session visits:</strong> <?= $_SESSION['visits'] ?></p>
    <form method="POST">
        <input type="text" name="name" placeholder="Enter your name" required>
        <button type="submit">Submit</button>
    </form>
    <?php if ($name): ?>
        <p>Hello, <strong><?= $name ?></strong>!</p>
    <?php endif; ?>
</body>
</html>
