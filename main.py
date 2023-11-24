import cv2
from pyzbar.pyzbar import decode
import webbrowser
import vk_api
import requests
import docx

ACCESS_TOKEN = 'vk1.a.Oq1QERzZ6-be2HQqN88Uk3yVcQIo5Pnf_ZovIZOeydTDYmfHg_J93yCw49x034miFCjvUiBkQUkOK6td3HOM3Q8yPnVW538tNREI1NO63385Yy2kM5fBh-Xc1wTIe2CHNVxD70MqVrFZl1cJhNMZrnvY8ILFIUh3GnP0SdP1QAmDom6pVkaRaplFLopiVXhopLPwPK4h_ZarLF2dQuwxqg'

#https://oauth.vk.com/authorize?client_id=51789300&display=page&redirect_uri=https://vk.com/public217355336&scope=friends,wall,photos&response_type=token&v=5.154&state=123456


def read_data_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        data = [(int(group_id), qr.strip()) for group_id, qr in (line.split(',') for line in lines)]
    return data


token_group_qr_pairs = read_data_from_file('data/IdAndQr.txt')
post_links = {}

# Функция для сканирования QR-кода и выполнения действий
def scan_and_execute_actions(group_id):
    # Опубликовать новость на стене группы перед сканированием QR-кода
    session = vk_api.VkApi(token=ACCESS_TOKEN)
    api = session.get_api()
    image_url = 'post/1.jpeg'
    message = ''
    doc = docx.Document("post/1.docx")
    all_paras = doc.paragraphs

    for para in all_paras:
        message = message + para.text + '\n\n'

    upload_url = api.photos.getWallUploadServer(group_id=group_id)['upload_url']

    with open(image_url, 'rb') as photo_file:
        upload_response = requests.post(upload_url, files={'photo': photo_file}).json()

    photo_data = api.photos.saveWallPhoto(group_id=group_id, server=upload_response['server'],
                                          photo=upload_response['photo'], hash=upload_response['hash'])

    # Получение ID сохраненной фотографии
    photo_id = f"photo{photo_data[0]['owner_id']}_{photo_data[0]['id']}"

    response = api.wall.post(owner_id=-abs(group_id), attachments=photo_id, message=message, from_group=1)

    if response.get('post_id'):
        post_id = response['post_id']
        post_link = f'https://vk.com/wall-{group_id}_{post_id}'
        post_links[(ACCESS_TOKEN, group_id)] = post_link
        print(f'Posted news in group {group_id}, post link: {post_link}')


def qr_scan(qr_code_path):
    image = cv2.imread(qr_code_path)
    decoded_objects = decode(image)

    if decoded_objects is not None:
        for obj in decoded_objects:
            url = obj.data.decode("utf-8")
            print(f'Type: {obj.type}, Data: {url}')

            headers = {
                'User-Agent': 'Locale.US, "VKAndroidApp/%s-%d (Android %s; SDK %d; %s; %s %s; %s)", new Object[] { PackageInfo.versionName, PackageInfo.versionCode, Build.VERSION.RELEASE, Integer.valueOf(Build.VERSION.SDK_INT), Build.CPU_ABI, Build.MANUFACTURER, Build.MODEL, System.getProperty("user.language") })'}
            response = requests.get(url, headers=headers)
            webbrowser.open(response.url, new=2, autoraise=True)
    else:
        print('QR-код не обнаружен на изображении.')


def save_post_links_to_file(post_links, file_path):
    with open(file_path, 'w') as file:
        for pair, post_link in post_links.items():
            line = f'{post_link}\n'
            file.write(line)

    print(f'Post links saved to {file_path}')


for group_id,qr  in token_group_qr_pairs:
    scan_and_execute_actions(group_id)

for group_id,qr  in token_group_qr_pairs:
    qr_scan(qr)

save_post_links_to_file(post_links, 'post_links.txt')



