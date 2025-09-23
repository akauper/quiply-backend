from whisper import DecodingOptions, DecodingResult

from src.framework.exceptions import ConversionException
from ...models import SpeechToTextGenerationParams, SpeechToTextResponse


class WhisperGenerationConverter:
    """
    A class for converting between Quiply and Whisper objects.

    :raises ConversionException: If the conversion fails.
    """

    @staticmethod
    def to_decoding_options(
            generation_params: SpeechToTextGenerationParams,
    ) -> DecodingOptions:
        """
        Convert a Quiply AudioGenerationParams to a Whisper DecodingOptions.

        :param generation_params: The Quiply AudioGenerationParams to convert.

        :return: The converted Whisper DecodingOptions.
        """

        try:
            params_dict = generation_params.model_dump(exclude_none=True)
            if 'max_tokens' in params_dict:
                params_dict['sample_len'] = params_dict['max_tokens']
                del params_dict['max_tokens']

            if 'device' in params_dict:
                params_dict.setdefault('fp16', params_dict['device'] == 'cuda')
                del params_dict['device']

            if 'model' in params_dict:
                del params_dict['model']

            return DecodingOptions(**params_dict)
        except Exception as e:
            raise ConversionException(
                WhisperGenerationConverter,
                from_type=SpeechToTextGenerationParams,
                to_type=DecodingOptions,
                inner_exception=e
            )

    @staticmethod
    def from_decoding_result(
            result: DecodingResult,
    ) -> SpeechToTextResponse:
        """
        Convert a Whisper DecodingResult to a Quiply SpeechToTextResponse.

        :param result: The Whisper DecodingResult to convert.

        :return: The converted Quiply SpeechToTextResponse.
        """

        try:
            return SpeechToTextResponse(
                text=result.text,
                language=result.language,
                language_probs=result.language_probs,
                tokens=result.tokens,
                avg_logprob=result.avg_logprob,
                no_speech_prob=result.no_speech_prob,
                temperature=result.temperature,
                compression_ratio=result.compression_ratio,
            )
        except Exception as e:
            raise ConversionException(
                WhisperGenerationConverter,
                from_type=DecodingResult,
                to_type=SpeechToTextResponse,
                inner_exception=e
            )