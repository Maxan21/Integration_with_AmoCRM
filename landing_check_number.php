<?php
'''
Суть: оставляется заявка клиента на лендинге, необходимо, во избежание дубля сделки, 
проверять есть ли уже в базе этот номер, и открыта ли по нему на данный момент сделка
Представлена только часть кода, отвечающая за проверку.
'''
require_once 'access.php';

echo "<body>";
header("Content-Type: text/html; charset=utf-8");
ob_end_flush();
$hostname = '';
$username = '';
$passwordname = '';
$basename = '';

$data_connect = mysqli_connect($hostname, $username, $passwordname, $basename);
if ($data_connect == false) {
    die("Ошибка: Невозможно подключиться к MySQL " . mysqli_connect_error());
} else {
    echo "Соединение установлено успешно";
}

mysqli_set_charset($data_connect, "utf8");

$phone_for_sql = mysqli_real_escape_string($data_connect, $phone); // Защита от SQL-инъекций
$sql = 'SELECT id_contact FROM contacts WHERE number="' . $phone_for_sql . '"';

$result_sql = mysqli_query($data_connect, $sql);
if ($result_sql==null) {
	die("Ошибка выполнения запроса: " . mysqli_error($data_connect));
}

$rows = mysqli_fetch_all($result_sql, MYSQLI_ASSOC);
$flag = 0;
foreach ($rows as $row) {
	$id_contact = $row['id_contact'];

	$headers = [
		'Content-Type: application/json',
		'Authorization: Bearer ' . $access_token,
	];

	$params = [
		'with' => 'leads'
	];
	$curl = curl_init();
	curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
	curl_setopt($curl, CURLOPT_URL, 'https://itnw.amocrm.ru/api/v4/contacts/'.$id_contact.'?with=leads');
	curl_setopt($curl, CURLOPT_CUSTOMREQUEST, 'GET');
	curl_setopt($curl, CURLOPT_POSTFIELDS, json_encode($params));
	curl_setopt($curl, CURLOPT_HTTPHEADER, $headers);
	curl_setopt($curl, CURLOPT_HEADER, false);
	curl_setopt($curl, CURLOPT_COOKIEFILE, 'cookie.txt');
	curl_setopt($curl, CURLOPT_COOKIEJAR, 'cookie.txt');
	curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, 0);
	curl_setopt($curl, CURLOPT_SSL_VERIFYHOST, 0);

	$out = curl_exec($curl);
	$code = curl_getinfo($curl, CURLINFO_HTTP_CODE);
	$code = (int) $code;
	

	if ($code < 200 || $code > 204) die("Error $code. " . (isset($errors[$code]) ? $errors[$code] : 'Undefined error'));
	
	
	$result_contact = json_decode($out, true);
	$leads = $result_contact['_embedded']['leads'];
	foreach ($leads as $lead) {
		$lead['id'];
		$leads_id = $lead['id'];
		$curl = curl_init();
		curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
		curl_setopt($curl, CURLOPT_URL, "https://itnw.amocrm.ru/api/v4/leads/" . $leads_id);
		curl_setopt($curl, CURLOPT_CUSTOMREQUEST, 'GET');
		curl_setopt($curl, CURLOPT_HTTPHEADER, $headers);
		curl_setopt($curl, CURLOPT_HEADER, false);
		curl_setopt($curl, CURLOPT_COOKIEFILE, 'cookie.txt');
		curl_setopt($curl, CURLOPT_COOKIEJAR, 'cookie.txt');
		curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, 0);
		curl_setopt($curl, CURLOPT_SSL_VERIFYHOST, 0);
		$out = curl_exec($curl);
		$code = curl_getinfo($curl, CURLINFO_HTTP_CODE);
		$code = (int) $code;
		$result_lead = json_decode($out, true);
		$responsible_user_id = $result_lead['responsible_user_id'];
		if ($result_lead['status_id'] != 143 && $result_lead['status_id'] != 142) {
			$time=intval(time());
			$data_for_tasks =$data_for_tasks = [
				[
				'responsible_user_id' => $responsible_user_id,
				'entity_type' => 'leads',
				'entity_id' => $leads_id,
				'text' => 'Срочно перезвонить на номер ' . $phone,
				'complete_till' => $time
				]
			];
			$curl = curl_init();
			curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
			curl_setopt($curl, CURLOPT_URL, "https://itnw.amocrm.ru/api/v4/tasks");
			curl_setopt($curl, CURLOPT_CUSTOMREQUEST, 'POST');
			curl_setopt($curl, CURLOPT_POSTFIELDS, json_encode($data_for_tasks));
			curl_setopt($curl, CURLOPT_HTTPHEADER, $headers);
			curl_setopt($curl, CURLOPT_HEADER, false);
			curl_setopt($curl, CURLOPT_COOKIEFILE, 'cookie.txt');
			curl_setopt($curl, CURLOPT_COOKIEJAR, 'cookie.txt');
			curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, 0);
			curl_setopt($curl, CURLOPT_SSL_VERIFYHOST, 0);
			$out = curl_exec($curl);
			$code = curl_getinfo($curl, CURLINFO_HTTP_CODE);
			$code = (int) $code;
			$result_post = json_decode($out, true);
			print_r($result_post);
			$flag = 1;
			break;
		}
	}	
}

if ($flag==0){
	$method = "/api/v4/leads/complex";

	$headers = [
		'Content-Type: application/json',
		'Authorization: Bearer ' . $access_token,
	];
	
	$curl = curl_init();
	curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
	curl_setopt($curl, CURLOPT_USERAGENT, 'amoCRM-API-client/1.0');
	curl_setopt($curl, CURLOPT_URL, "https://$subdomain.amocrm.ru" . $method);
	curl_setopt($curl, CURLOPT_CUSTOMREQUEST, 'POST');
	curl_setopt($curl, CURLOPT_POSTFIELDS, json_encode($data));
	curl_setopt($curl, CURLOPT_HTTPHEADER, $headers);
	curl_setopt($curl, CURLOPT_HEADER, false);
	curl_setopt($curl, CURLOPT_COOKIEFILE, 'cookie.txt');
	curl_setopt($curl, CURLOPT_COOKIEJAR, 'cookie.txt');
	curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, 0);
	curl_setopt($curl, CURLOPT_SSL_VERIFYHOST, 0);
	$out = curl_exec($curl);
	$code = curl_getinfo($curl, CURLINFO_HTTP_CODE);
	$code = (int) $code;
	
	$errors = [
		301 => 'Moved permanently.',
		400 => 'Wrong structure of the array of transmitted data, or invalid identifiers of custom fields.',
		401 => 'Not Authorized. There is no account information on the server. You need to make a request to another server on the transmitted IP.',
		403 => 'The account is blocked, for repeatedly exceeding the number of requests per second.',
		404 => 'Not found.',
		500 => 'Internal server error.',
		502 => 'Bad gateway.',
		503 => 'Service unavailable.'
	];
	
	if ($code < 200 || $code > 204) die("Error $code. " . (isset($errors[$code]) ? $errors[$code] : 'Undefined error'));
	
	$result = json_decode($out, true);
	$leadId = $result[0]['id']; // Получение ID созданной сделки
	
	$note_str = '
	Страница: ' . $title . '
	Имя: ' . $name . '
	Телефон: ' . $phone . '
	Регион: ' . $region . '
	';
	
	($_POST['region']) ? $region = $_POST['region'] : $region = '';
	$name = $_POST['name'];
	$phone = $_POST['phone'];
	$yclid = $_POST['yclid'];
	$_ym_uid = $_POST['_ym_uid'];
	$utm_source = $_POST['utm_source'];
	$utm_campaign = $_POST['utm_campaign'];
	$utm_content = $_POST['utm_content'];
	$utm_term = $_POST['utm_term'];
	
	// Данные для примечания
	$notesData = [
		[
			"entity_id" => $leadId,
			"note_type" => "common", // В зависимости от типа примечания, можно изменить на другой тип
			"params" => [
				"text" => $note_str
			],
		],
	];
	
	// Добавление примечания к созданной сделке
	$notesMethod = "/api/v4/leads/notes";
	
	$curl = curl_init();
	curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
	curl_setopt($curl, CURLOPT_USERAGENT, 'amoCRM-API-client/1.0');
	curl_setopt($curl, CURLOPT_URL, "https://$subdomain.amocrm.ru" . $notesMethod);
	curl_setopt($curl, CURLOPT_CUSTOMREQUEST, 'POST');
	curl_setopt($curl, CURLOPT_POSTFIELDS, json_encode($notesData));
	curl_setopt($curl, CURLOPT_HTTPHEADER, $headers);
	curl_setopt($curl, CURLOPT_HEADER, false);
	curl_setopt($curl, CURLOPT_COOKIEFILE, 'cookie.txt');
	curl_setopt($curl, CURLOPT_COOKIEJAR, 'cookie.txt');
	curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, 0);
	curl_setopt($curl, CURLOPT_SSL_VERIFYHOST, 0);
	$out = curl_exec($curl);
	$code = curl_getinfo($curl, CURLINFO_HTTP_CODE);
	$code = (int) $code;
	
	error_log($out, 0);
	
	$errors = [
		301 => 'Moved permanently.',
		400 => 'Wrong structure of the array of transmitted data, or invalid identifiers of custom fields.',
		401 => 'Not Authorized. There is no account information on the server. You need to make a request to another server on the transmitted IP.',
		403 => 'The account is blocked, for repeatedly exceeding the number of requests per second.',
		404 => 'Not found.',
		500 => 'Internal server error.',
		502 => 'Bad gateway.',
		503 => 'Service unavailable.'
	];
	
	if ($code < 200 || $code > 204) die("Error $code. " . (isset($errors[$code]) ? $errors[$code] : 'Undefined error'));
}
