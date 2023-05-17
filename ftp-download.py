import os
from ftplib import FTP, error_perm
import time


def display_progress(block, local_file, total_size,current_time):
    local_file.write(block)
    global block_count, prev_time
    # downloaded = block_count * 1024
    downloaded = local_file.tell()
    progress = min(float(downloaded) / total_size, 1.0)
    progress_percent = round(progress * 100, 2)
    speed = 0.001024 / (current_time - prev_time)
    prev_time = current_time
    filename = local_file.name
    print(f"Downloading: {filename} - {progress_percent}% ({speed:.2f} Mb/s)", end='\r', flush=True)

    block_count += 1


def download_files_from_ftp(ftp, directory, path):
    global block_count, prev_time
    file_list = []
    path = os.path.join(path, directory)
    # print('1', ftp.pwd())
    downloaded_size = 0
    ftp.cwd(directory)
    ftp.retrlines('LIST', lambda line: file_list.append(line.split()))
    for fd in file_list:
        count = 0
        file = fd[-1]
        if fd[0].startswith('d'):
            count += download_files_from_ftp(ftp, file, path)
        elif file.endswith('.mzML'):
            if (directory + '-' + file) in downloaded_file_list:
                print(f'Skipped: {file} (already downloaded)')
                continue

            if not os.path.exists(path):
                os.makedirs(path)
            if os.path.exists(os.path.join(path, file)):
                downloaded_size = os.path.getsize(os.path.join(path, file))
                ftp.sendcmd('TYPE I')

            with open(os.path.join(path, file), 'wb') as local_file:
                file_size = int(fd[4])
                if downloaded_size >= file_size:
                    print(f'Skipped: {file} (already downloaded)')
                    block_count = 1
                    with open('downloaded_file_list.txt', 'a') as resume:
                        resume.write(directory + '-' + file + '\n')
                    count += 1
                    continue

                ftp.sendcmd(f'REST {downloaded_size}')
                local_file.seek(downloaded_size)
                try:
                    prev_time = time.time()
                    ftp.retrbinary('RETR ' + file, lambda block: display_progress(block, local_file, file_size,time.time()), 1024)
                except error_perm as e:
                    print(f"Error: {e}")

                print(f'Downloaded: {file}')
                block_count = 1
                with open('downloaded_file_list.txt', 'a') as resume:
                    resume.write(directory + '-' + file + '\n')
                count += 1
    # print('2', ftp.pwd())
    # ftp.cwd('..')

    return count


def main():
    ftp_host = 'ftp.ebi.ac.uk'
    ftp = FTP(ftp_host)
    ftp.login()
    ftp.cwd('/pub/databases/metabolights/studies/public/')

    for directory in download_list:
        # print('3', ftp.pwd())
        if directory in downloaded_directory_list:
            print(f'Skipped: {directory} (already downloaded)')
            continue
        else:
            if download_files_from_ftp(ftp, directory, local_path) > 0:
                print(f'Downloaded {directory}')
                with open('downloaded_file_list.txt', 'a') as downloaded:
                    downloaded.write(directory + '\n')
            else:
                print(f'no mzML file')
                with open('failed_directory.txt', 'a') as failed:
                    failed.write(directory + '\n')

    ftp.quit()
    print('All files downloaded.')


if __name__ == '__main__':
    downloaded_file_list = []
    download_list = []
    downloaded_directory_list = []
    failed_directory_list = 'failed_directory.txt'
    local_path = 'Downloads'
    block_count = 1
    prev_time = None
    with open('downloaded_file_list.txt', 'r') as list1:
        downloaded_file_list = [line.strip() for line in list1]
    with open('download_list.txt', 'r') as list2:
        download_list = [line.strip() for line in list2]
    with open("downloaded_directory_list.txt", 'r') as list3:
        downloaded_directory_list = [line.strip() for line in list3]
    main()
