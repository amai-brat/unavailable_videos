from urllib.parse import urlparse, parse_qs
from roflan import get_parsed_playlist
import json
import os


def show_difference_between_backups(m: int, n: int):
    print('<->')
    print('Playlist: ' + m['playlist_id'])
    print('Newer backup: ' + m['date'])
    print('Older backup: ' + n['date'] + '\n')
    
    diff_pros = set(m['items']) - set(n['items'])
    diff_cons = set(n['items']) - set(m['items'])
    modified = set(m['items']) & set(n['items'])
    for video_id in sorted(diff_pros, key=lambda x: m['items'][x]['id']):
        print(f"+++ {m['items'][video_id]['id']:4}|https://www.youtube.com/watch?v={video_id}: {m['items'][video_id]['title']}")
    
    for video_id in sorted(diff_cons, key=lambda x: n['items'][x]['id']):
        print(f"--- {n['items'][video_id]['id']:4}|https://www.youtube.com/watch?v={video_id}: {n['items'][video_id]['title']}")
    
    for video_id in sorted(modified, key=lambda x: m['items'][x]['id']):
        if video_id in n['items']:
            if m['items'][video_id]['title'] != n['items'][video_id]['title']:
                print(f"*** {m['items'][video_id]['id']:4}|https://www.youtube.com/watch?v={video_id}: {m['items'][video_id]['title']:69} <> {n['items'][video_id]['title']}")
    print('<->')


def show_unavailable_videos(curr: dict):
    print('<->')
    reasons = ['Deleted video', 'Private video', '[Deleted video]', '[Private video]']
    for video_id in curr['items']:
        if curr['items'][video_id]['title'] in reasons:
            print('{:04}: {} https://www.youtube.com/watch?v={}'.format(*curr['items'][video_id].values(), video_id))
    print('<->')


def playlist_url_handler(url: str):
    d = urlparse(url).query
    if d:
        return parse_qs(d)['list'][0]
    return url


def existing_playlists_in_path(path: str = '.'):
    return sorted(set([x[9:-10] for x in os.listdir(path) if x.startswith('playlist_') and x.endswith('.json')]))


def main():
    PLAYLIST_ID = ''
    fapah = existing_playlists_in_path()
    if fapah:
        print('Playlists, which have backups: ')
        _k = 0
        for pl in fapah:
            _k += 1
            print(f'#{_k}. {pl}')
        playlist = input('Enter num (e.g. #1, #2) or something else, if you want to add new playlist: ')
        if playlist and playlist[0] == '#':
            PLAYLIST_ID = fapah[(int(playlist[1:])-1)%len(fapah)]
    if not PLAYLIST_ID:
        playlist = input('Enter playlist id or url: ')
        PLAYLIST_ID = playlist_url_handler(playlist)
        while len(PLAYLIST_ID) != 34:
            print('Try again')
            playlist = input('Enter playlist id or url: ')
            PLAYLIST_ID = playlist_url_handler(playlist)

    backup_yes_no = input('Make new backup: [y/n] ')
    try:
        k = max([int(file.split('_')[-1][:4]) for file in os.listdir() if file.startswith(f'playlist_{PLAYLIST_ID}_')])
    except:
        k = 0
    if backup_yes_no and (backup_yes_no[0] == 'y' or backup_yes_no == '1'):
        print('Wait...')
        k += 1
        parsed_playlist = get_parsed_playlist(PLAYLIST_ID,show=True)
        curr_file = open(f'playlist_{PLAYLIST_ID}_{k:04}.json', 'w')
        json.dump(parsed_playlist, curr_file, indent=4, ensure_ascii=False)
        curr_file.close()
    str_for_input = 'Enter number: \n1. Show differences between current playlist backup and previous\n2. Show unavailable videos now\n3. Show differences between m and n backups (m>n)\nor [Enter] for exit\n>>> '
    choice = input(str_for_input)
    while choice:
        if not choice.isdigit():
            break
        match int(choice):
            case 1:   
                try:
                    curr = json.load(open(f'playlist_{PLAYLIST_ID}_{k:04}.json'))
                    prev = json.load(open(f'playlist_{PLAYLIST_ID}_{k-1:04}.json'))
                except:
                    print('Need for Backup')
                    break
                show_difference_between_backups(curr, prev)
            case 2:
                try:
                    curr = json.load(open(f'playlist_{PLAYLIST_ID}_{k:04}.json'))
                except:
                    print('Need for Backup')
                    break
                show_unavailable_videos(curr)
            case 3:
                playlist_nums = sorted([int(file.split('_')[-1][:4]) for file in os.listdir() if file.startswith(f'playlist_{PLAYLIST_ID}_')])
                if playlist_nums:
                    try:
                        m = int(input(f'Choose m => {playlist_nums}: '))%(k+1)
                        n = int(input(f'Choose n => {playlist_nums}: '))%(k+1)
                    except ValueError:
                        print('m, n are int')
                        break
                    if n>m: m,n = n,m
                else:
                    print('Need for Backup')
                    break
                f_m = json.load(open(f'playlist_{PLAYLIST_ID}_{m:04}.json'))
                f_n = json.load(open(f'playlist_{PLAYLIST_ID}_{n:04}.json'))
                show_difference_between_backups(f_m, f_n)

        choice = input(str_for_input)


if __name__ == '__main__':
    main()
