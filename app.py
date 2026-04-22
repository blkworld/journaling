ydl_opts = {
                    # Ambil video & audio terbaik apa pun formatnya, lalu gabung jadi mp4
                    'format': 'bestvideo+bestaudio/best',
                    'merge_output_format': 'mp4',
                    'outtmpl': 'downloaded_video.%(ext)s',
                    'cookiefile': 'cookies.txt',
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'quiet': True,
                    'no_warnings': True,
                    'nocheckcertificate': True,
                    # Paksa konversi ke mp4 jika format asal bukan mp4
                    'postprocessors': [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4',
                    }],
                }
