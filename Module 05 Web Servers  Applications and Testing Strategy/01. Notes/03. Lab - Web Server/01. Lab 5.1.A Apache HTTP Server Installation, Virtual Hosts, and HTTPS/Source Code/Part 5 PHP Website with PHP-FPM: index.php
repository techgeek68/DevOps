<?php
session_start();

$className = "Grade 10, Section B";
$teacher = $_SESSION['teacher'] ?? "Mrs. Sunita Rana";
$today = date("Y-m-d");
$recordFile = "/var/www/attendance/records/{$today}.txt";

$roll = [
    101 => "Anup Ghimire",
    102 => "Bipana Thapa",
    103 => "Deepak Karki",
    104 => "Kritika Basnet",
    105 => "Manisha Rai",
    106 => "Nabin Shrestha",
    107 => "Pratik Lama",
    108 => "Rojina Magar",
    109 => "Sagar Bhandari",
    110 => "Tara Devkota",
];

$saved = [];
if (file_exists($recordFile)) {
    foreach (file($recordFile, FILE_IGNORE_NEW_LINES) as $line) {
        [$rollNo, $status] = explode("|", $line, 2);
        $saved[(int)$rollNo] = $status;
    }
}

$message = "";
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $lines = [];
    foreach ($roll as $rollNo => $studentName) {
        $status = $_POST['status'][$rollNo] ?? 'Absent';
        $status = in_array($status, ['Present', 'Absent', 'Late'], true) ? $status : 'Absent';
        $lines[] = $rollNo . "|" . $status;
        $saved[$rollNo] = $status;
    }
    file_put_contents($recordFile, implode(PHP_EOL, $lines) . PHP_EOL);
    $message = "Attendance for {$today} has been saved.";
}

$presentCount = count(array_filter($saved, fn($s) => $s === 'Present'));
$absentCount = count(array_filter($saved, fn($s) => $s === 'Absent'));
$lateCount = count(array_filter($saved, fn($s) => $s === 'Late'));
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shree Kalika Secondary School | Attendance Register</title>
    <style>
        :root {
            --maroon: #6e1423;
            --gold: #c9a24b;
            --paper: #faf6ee;
            --ink: #2b2118;
        }
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: 'Georgia', 'Times New Roman', serif;
            background: var(--paper);
            color: var(--ink);
        }
        header.register-band {
            background: var(--maroon);
            color: var(--gold);
            padding: 1.4rem 2rem;
            border-bottom: 6px solid var(--gold);
        }
        header.register-band h1 {
            margin: 0;
            font-size: 1.6rem;
            letter-spacing: 0.04em;
        }
        header.register-band p {
            margin: 0.3rem 0 0;
            color: #f1e3c6;
            font-size: 0.95rem;
        }
        main {
            max-width: 780px;
            margin: 2rem auto;
            padding: 0 1.2rem 2rem;
        }
        .meta-strip {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 0.6rem;
            background: #fff;
            border: 1px solid #ddcdaa;
            border-left: 6px solid var(--maroon);
            padding: 0.9rem 1.1rem;
            margin-bottom: 1.4rem;
            font-size: 0.95rem;
        }
        table.roll {
            width: 100%;
            border-collapse: collapse;
            background: #fff;
            border: 1px solid #ddcdaa;
        }
        table.roll caption {
            text-align: left;
            font-size: 1.1rem;
            padding: 0.6rem 0.2rem;
            font-weight: bold;
            color: var(--maroon);
        }
        table.roll th {
            background: var(--maroon);
            color: var(--gold);
            text-align: left;
            padding: 0.6rem 0.7rem;
            font-size: 0.9rem;
        }
        table.roll td {
            padding: 0.55rem 0.7rem;
            border-top: 1px solid #eee0c4;
            font-size: 0.95rem;
        }
        table.roll tr:nth-child(even) td {
            background: #fbf3df;
        }
        .mark-group {
            display: flex;
            gap: 0.9rem;
        }
        .mark-group label {
            display: flex;
            align-items: center;
            gap: 0.3rem;
            cursor: pointer;
            font-size: 0.85rem;
            padding: 0.2rem 0.5rem;
            border-radius: 999px;
            border: 1px solid #ddcdaa;
        }
        .mark-group input { accent-color: var(--maroon); }
        .save-row {
            margin-top: 1.2rem;
            text-align: right;
        }
        button.save {
            background: var(--maroon);
            color: var(--gold);
            border: none;
            padding: 0.65rem 1.6rem;
            font-size: 1rem;
            border-radius: 3px;
            cursor: pointer;
            font-family: inherit;
        }
        button.save:hover {
            background: #57101c;
        }
        .tally {
            margin-top: 1.6rem;
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }
        .tally div {
            flex: 1;
            min-width: 140px;
            background: #fff;
            border: 1px solid #ddcdaa;
            border-top: 4px solid var(--maroon);
            padding: 0.7rem 0.9rem;
            text-align: center;
        }
        .tally span {
            display: block;
            font-size: 1.6rem;
            font-weight: bold;
            color: var(--maroon);
        }
        .flash {
            background: #eef6ea;
            border: 1px solid #b8dcae;
            color: #234b1a;
            padding: 0.6rem 0.9rem;
            margin-bottom: 1.2rem;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <header class="register-band">
        <h1>Shree Kalika Secondary School</h1>
        <p>Daily Attendance Register</p>
    </header>
    <main>
        <div class="meta-strip">
            <span><strong>Class:</strong> <?= htmlspecialchars($className) ?></span>
            <span><strong>Subject Teacher:</strong> <?= htmlspecialchars($teacher) ?></span>
            <span><strong>Date:</strong> <?= htmlspecialchars($today) ?></span>
            <span><strong>Server:</strong> <?= htmlspecialchars($_SERVER['SERVER_NAME']) ?> (PHP <?= PHP_VERSION ?>)</span>
        </div>

        <?php if ($message): ?>
            <div class="flash"><?= htmlspecialchars($message) ?></div>
        <?php endif; ?>

        <form method="POST">
            <table class="roll">
                <caption>Class Roll</caption>
                <thead>
                    <tr>
                        <th>Roll No.</th>
                        <th>Student Name</th>
                        <th>Mark</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($roll as $rollNo => $studentName): ?>
                        <?php $current = $saved[$rollNo] ?? 'Present'; ?>
                        <tr>
                            <td><?= $rollNo ?></td>
                            <td><?= htmlspecialchars($studentName) ?></td>
                            <td>
                                <div class="mark-group">
                                    <?php foreach (['Present', 'Late', 'Absent'] as $option): ?>
                                        <label>
                                            <input type="radio" name="status[<?= $rollNo ?>]" value="<?= $option ?>" <?= $current === $option ? 'checked' : '' ?>>
                                            <?= $option ?>
                                        </label>
                                    <?php endforeach; ?>
                                </div>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
            <div class="save-row">
                <button type="submit" class="save">Save Attendance</button>
            </div>
        </form>

        <div class="tally">
            <div>Present<span><?= $presentCount ?></span></div>
            <div>Late<span><?= $lateCount ?></span></div>
            <div>Absent<span><?= $absentCount ?></span></div>
        </div>
    </main>
</body>
</html>
