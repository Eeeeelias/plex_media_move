# testing stuff out
import subprocess


def check_ffmpeg():
    try:
        status, _ = subprocess.getstatusoutput("ffmpeg -version")
        print(status)
        if status == 0:
            return True
        return False
    except Exception:
        print("error")


if __name__ == '__main__':
    print(check_ffmpeg())
