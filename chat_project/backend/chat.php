<?php
session_start();
header('Content-Type: application/json');

// Получаем входные данные (JSON)
$input = file_get_contents('php://input');
$data = json_decode($input, true);

// Проверяем наличие сообщения
if (!isset($data['message'])) {
    echo json_encode(['success' => false, 'error' => 'Нет сообщения']);
    exit;
}

$message = trim($data['message']);
if (strlen($message) === 0 || strlen($message) > 1000) {
    echo json_encode(['success' => false, 'error' => 'Сообщение должно содержать от 1 до 1000 символов']);
    exit;
}

// Настройки для API OpenAI
$apiKey = 'YOUR_OPENAI_API_KEY_HERE'; // Замените на ваш API key
$apiUrl = 'https://api.openai.com/v1/chat/completions';

// Формируем данные для запроса (например, используя модель gpt-3.5-turbo)
$postData = [
    'model' => 'gpt-3.5-turbo',
    'messages' => [
        ['role' => 'user', 'content' => $message]
    ],
    'max_tokens' => 1000,
    'temperature' => 0.7,
];

$ch = curl_init($apiUrl);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'Authorization: Bearer ' . $apiKey
]);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($postData));
curl_setopt($ch, CURLOPT_TIMEOUT, 15); // Тайм-аут 15 секунд

$response = curl_exec($ch);

if (curl_errno($ch)) {
    $error_msg = curl_error($ch);
    curl_close($ch);
    echo json_encode(['success' => false, 'error' => 'cURL Error: ' . $error_msg]);
    exit;
}

curl_close($ch);

$result = json_decode($response, true);
if (!isset($result['choices'][0]['message']['content'])) {
    echo json_encode(['success' => false, 'error' => 'Некорректный ответ API']);
    exit;
}

$reply = trim($result['choices'][0]['message']['content']);

// Ограничиваем длину ответа до 1000 символов, если необходимо
if (strlen($reply) > 1000) {
    $reply = substr($reply, 0, 1000);
}

echo json_encode(['success' => true, 'response' => $reply]);
exit;
?>
