import os
import tempfile
import time
from typing import Dict

import dashscope
from dashscope.audio.asr import (Recognition)
from pydub import AudioSegment
from pydub.utils import which

from setting.models_provider.base_model_provider import MaxKBBaseModel
from setting.models_provider.impl.base_stt import BaseSpeechToText


class AliyunBaiLianSpeechToText(MaxKBBaseModel, BaseSpeechToText):
    api_key: str
    model: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.model = kwargs.get('model')

    @staticmethod
    def safe_remove_file(file_path, max_retries=3, delay=0.1):
        """
        安全删除文件，处理文件被占用的情况
        """
        for attempt in range(max_retries):
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    return True
            except (PermissionError, OSError) as e:
                if attempt < max_retries - 1:
                    time.sleep(delay * (2 ** attempt))  # 指数退避
                    continue
                else:
                    # 最后一次尝试失败，记录错误但不抛出异常
                    print(f"警告：无法删除临时文件 {file_path}: {e}")
                    return False
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {}
        if 'max_tokens' in model_kwargs and model_kwargs['max_tokens'] is not None:
            optional_params['max_tokens'] = model_kwargs['max_tokens']
        if 'temperature' in model_kwargs and model_kwargs['temperature'] is not None:
            optional_params['temperature'] = model_kwargs['temperature']
        if model_name == 'qwen-omni-turbo':
            optional_params['streaming'] = True
        return AliyunBaiLianSpeechToText(
            model=model_name,
            api_key=model_credential.get('api_key'),
        )

    def check_auth(self):
        cwd = os.path.dirname(os.path.abspath(__file__))
        with open(f'{cwd}/iat_mp3_16k.mp3', 'rb') as f:
            self.speech_to_text(f)

    def _ensure_ffmpeg_available(self):
        """确保本机可用 ffmpeg 与 ffprobe，否则抛出友好错误。增加诊断信息。"""
        import subprocess
        import shutil
        print('当前PATH:', os.environ.get('PATH'))
        ffmpeg = which('ffmpeg')
        ffprobe = which('ffprobe')
        print('pydub.which ffmpeg:', ffmpeg)
        print('pydub.which ffprobe:', ffprobe)
        if not ffmpeg:
            ffmpeg = shutil.which('ffmpeg')
            print('shutil.which ffmpeg:', ffmpeg)
        if not ffprobe:
            ffprobe = shutil.which('ffprobe')
            print('shutil.which ffprobe:', ffprobe)
        if not ffmpeg:
            try:
                result = subprocess.run(['ffmpeg', '-version'],
                                        capture_output=True, text=True, timeout=5)
                print('subprocess ffmpeg:', result.returncode, result.stdout)
                if result.returncode == 0:
                    ffmpeg = 'ffmpeg'
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
                print('subprocess ffmpeg error:', e)
        if not ffprobe:
            try:
                result = subprocess.run(['ffprobe', '-version'],
                                        capture_output=True, text=True, timeout=5)
                print('subprocess ffprobe:', result.returncode, result.stdout)
                if result.returncode == 0:
                    ffprobe = 'ffprobe'
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
                print('subprocess ffprobe error:', e)
        # 如果还是找不到，尝试设置 AudioSegment.converter/ffprobe
        if not ffmpeg or not ffprobe:
            print(
                '未检测到 FFmpeg/FFprobe。请在 Windows 上安装 FFmpeg 并将其 bin 目录加入 PATH，或将可执行文件路径写入环境变量。下载地址: https://www.gyan.dev/ffmpeg/builds/ 安装后重启服务。')
            raise FileNotFoundError(
                '未检测到 FFmpeg/FFprobe。请在 Windows 上安装 FFmpeg 并将其 bin 目录加入 PATH，'
                '或将可执行文件路径写入环境变量。下载地址: https://www.gyan.dev/ffmpeg/builds/ '
                '安装后重启服务。')
        # 设置 pydub 的 converter 路径（可选，便于调试）
        AudioSegment.converter = ffmpeg
        AudioSegment.ffprobe = ffprobe
        print('最终使用 ffmpeg:', AudioSegment.converter)
        print('最终使用 ffprobe:', AudioSegment.ffprobe)

    def speech_to_text(self, audio_file):
        dashscope.api_key = self.api_key
        recognition = Recognition(model=self.model,
                                  format='mp3',
                                  sample_rate=16000,
                                  callback=None)

        # 预检查：FFmpeg/FFprobe 是否可用，避免 pydub 抛 WinError 2
        self._ensure_ffmpeg_available()

        temp_file_path = None
        converted_temp_path = None
        try:
            # 写入源音频到临时文件，离开 with 后句柄释放，避免 Windows 文件占用
            with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as temp_file:
                temp_file.write(audio_file.read())
                temp_file_path = temp_file.name

            # 读取并规范化音频（单声道、16kHz）
            audio = AudioSegment.from_file(temp_file_path)
            if audio.channels != 1:
                audio = audio.set_channels(1)
            if audio.frame_rate != 16000:
                audio = audio.set_frame_rate(16000)

            # 为转换后的音频创建仅路径（不保持打开），避免导出时文件被占用
            fd, converted_temp_path = tempfile.mkstemp(suffix='.mp3')
            os.close(fd)  # 立即关闭句柄，避免占用

            # 将转换后的音频文件保存到新的临时文件中
            audio.export(converted_temp_path, format='mp3')

            # 识别转换后的音频文件
            result = recognition.call(converted_temp_path)
            text = ''
            if result.status_code == 200:
                result_sentence = result.get_sentence()
                if result_sentence is not None:
                    for sentence in result_sentence:
                        text += sentence['text']
                return text
            else:
                raise Exception('Error: ', result.message)
        except Exception as e:
            # 可在此处加入日志记录（保持原逻辑抛出）
            raise e
        finally:
            # 安全删除临时文件
            if temp_file_path:
                self.safe_remove_file(temp_file_path)
            if converted_temp_path:
                self.safe_remove_file(converted_temp_path)
