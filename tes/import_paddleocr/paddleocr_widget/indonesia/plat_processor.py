"""
Indonesian License Plate Processor
Proses hasil deteksi OCR untuk validasi dan koreksi plat nomor Indonesia.

Struktur Plat Nomor Indonesia:
  [Huruf Wilayah] [Nomor Registrasi] [Huruf Seri]
  Contoh: B 1234 CD, BK 987 AB, D 12 A

Koreksi kesalahan umum:
  - Angka 0 ↔ Huruf O (berdasarkan posisi)
  - Angka 8 ↔ Huruf B
  - Angka 1 ↔ Huruf I atau l
  - Angka 5 ↔ Huruf S
  - Angka 2 ↔ Huruf Z
"""

import re
from typing import List, Dict, Optional, Tuple


class IndonesianPlateProcessor:
    """Processor untuk validasi dan koreksi plat nomor Indonesia."""

    def __init__(self):
        """Initialize processor."""
        # Mapping karakter yang sering tertukar
        self.confusing_chars = {
            'O': '0',  # O → 0 (di bagian angka)
            '0': 'O',  # 0 → O (di bagian huruf)
            'B': '8',  # B → 8 (di bagian angka)
            '8': 'B',  # 8 → B (di bagian huruf)
            'I': '1',  # I → 1 (di bagian angka)
            '1': 'I',  # 1 → I (di bagian huruf)
            'l': '1',  # l (lowercase L) → 1
            'S': '5',  # S → 5 (di bagian angka)
            '5': 'S',  # 5 → S (di bagian huruf)
            'Z': '2',  # Z → 2 (di bagian angka)
            '2': 'Z',  # 2 → Z (di bagian huruf)
            'G': '6',  # G → 6 (di bagian angka)
            '6': 'G',  # 6 → G (di bagian huruf)
            'Q': '9',  # Q → 9 (di bagian angka)
            '9': 'Q',  # 9 → Q (di bagian huruf)
        }

        # Kode wilayah valid di Indonesia (contoh)
        self.valid_region_codes = {
            # Single letter regions
            'A', 'B', 'D', 'E', 'F', 'G', 'H', 'K', 'L', 'M', 'N', 'P', 'R', 
            'S', 'T', 'U', 'W', 'X', 'Z',
            # Double letter regions
            'AA', 'AB', 'AD', 'AE', 'AG', 'BA', 'BB', 'BD', 'BE', 'BG', 'BH',
            'BK', 'BL', 'BM', 'BN', 'BP', 'BR', 'BS', 'DA', 'DB', 'DC', 'DD',
            'DE', 'DG', 'DH', 'DK', 'DL', 'DM', 'DN', 'DP', 'DR', 'DS', 'DT', 
            'DU', 'EA', 'EB', 'ED', 'EK', 'EL', 'EP', 'ES', 'ET', 'KB', 'KH', 
            'KT', 'KV', 'KY',
        }
        
        # Region codes yang TIDAK valid (biasanya OCR error dari huruf confusable)
        self.invalid_region_codes = {
            'BO', 'BI', 'BQ', 'B8', 'B0', 'B1', 'B5', 'B2', 'B6', 'B9',
            'DO', 'DI', 'DQ', 'D8', 'D0', 'D1', 'D5', 'D2', 'D6', 'D9',
            'FO', 'FI', 'FQ', 'F8', 'F0', 'F1', 'F5', 'F2', 'F6', 'F9',
            'GO', 'GI', 'GQ', 'G8', 'G0', 'G1', 'G5', 'G2', 'G6', 'G9',
            'HO', 'HI', 'HQ', 'H8', 'H0', 'H1', 'H5', 'H2', 'H6', 'H9',
            'KO', 'KI', 'KQ', 'K8', 'K0', 'K1', 'K5', 'K2', 'K6', 'K9',
            'LO', 'LI', 'LQ', 'L8', 'L0', 'L1', 'L5', 'L2', 'L6', 'L9',
            'MO', 'MI', 'MQ', 'M8', 'M0', 'M1', 'M5', 'M2', 'M6', 'M9',
            'NO', 'NI', 'NQ', 'N8', 'N0', 'N1', 'N5', 'N2', 'N6', 'N9',
            'PO', 'PI', 'PQ', 'P8', 'P0', 'P1', 'P5', 'P2', 'P6', 'P9',
            'RO', 'RI', 'RQ', 'R8', 'R0', 'R1', 'R5', 'R2', 'R6', 'R9',
            'SO', 'SI', 'SQ', 'S8', 'S0', 'S1', 'S5', 'S2', 'S6', 'S9',
            'TO', 'TI', 'TQ', 'T8', 'T0', 'T1', 'T5', 'T2', 'T6', 'T9',
            'WO', 'WI', 'WQ', 'W8', 'W0', 'W1', 'W5', 'W2', 'W6', 'W9',
            'ZO', 'ZI', 'ZQ', 'Z8', 'Z0', 'Z1', 'Z5', 'Z2', 'Z6', 'Z9',
        }

        # Huruf yang TIDAK boleh ada di seri (I dan Q biasanya tidak digunakan)
        self.invalid_series_chars = {'I', 'Q'}

    def parse_plate(self, text: str) -> Optional[Dict[str, str]]:
        """
        Parse teks menjadi komponen plat nomor.
        Mencoba berbagai kombinasi untuk menangani OCR errors.

        Logic:
        - Struktur: [Region 1-2 huruf] [Number 1-4 angka] [Series 0-3 huruf]
        - O/Ø di REGION → tetap huruf (region code)
        - O/Ø di NUMBER → jadi angka 0
        - O/Ø di SERIES → jadi huruf O

        Args:
            text: Teks hasil deteksi OCR

        Returns:
            Dictionary dengan keys: 'region', 'number', 'series' atau None jika tidak valid
        """
        # Bersihkan teks
        text = text.strip().upper()

        # Quick reject - must have at least 3 chars and not too long
        if len(text) < 3 or len(text) > 15:
            return None

        # Quick reject - must have at least 1 letter and 1 digit
        has_letter = any(c.isalpha() for c in text)
        has_digit = any(c.isdigit() for c in text)
        if not (has_letter and has_digit):
            return None

        # Pattern 1: [1-2 huruf] [spasi] [1-4 angka] [spasi] [0-3 huruf]
        pattern_with_space = r'^([A-Z]{1,2})\s*(\d{1,4})\s*([A-Z]{0,3})$'

        # Pattern 2: [1-2 huruf] [1-4 angka] [0-3 huruf] (tanpa spasi)
        pattern_no_space = r'^([A-Z]{1,2})(\d{1,4})([A-Z]{0,3})$'

        # Try with space first
        match = re.match(pattern_with_space, text)
        if match:
            region = match.group(1)
            number = match.group(2)
            series = match.group(3)

            # Check if region is valid and not an invalid code
            if region in self.valid_region_codes and region not in self.invalid_region_codes:
                return {
                    'region': region,
                    'number': number,
                    'series': series,
                    'original': text
                }

        # Try without space
        match = re.match(pattern_no_space, text)
        if match:
            region = match.group(1)
            number = match.group(2)
            series = match.group(3)
            
            # Check if region is valid and not an invalid code
            if region in self.valid_region_codes and region not in self.invalid_region_codes:
                return {
                    'region': region,
                    'number': number,
                    'series': series,
                    'original': text
                }

        # Try pre-correction for common OCR errors
        # Replace confusing letters in potential number positions

        # Pattern 3: Try to find pattern with letter→number correction
        # Replace O, Q, I, S, Z, B, G, J with numbers in the middle section
        for region_len in [1, 2]:
            for series_len in [0, 1, 2, 3]:
                if len(text) < region_len + 1 + series_len:
                    continue

                potential_region = text[:region_len]
                potential_series = text[-series_len:] if series_len > 0 else ''
                potential_number = text[region_len:len(text)-series_len] if series_len > 0 else text[region_len:]
                
                # Remove spaces from number section
                potential_number_clean = potential_number.replace(' ', '')

                # Check if region is valid (must be in valid list AND not in invalid list)
                if potential_region not in self.valid_region_codes:
                    continue

                # Skip if region is in invalid list (likely OCR error)
                if potential_region in self.invalid_region_codes:
                    continue

                # Series cannot be more than 3 characters
                if len(potential_series) > 3:
                    continue

                # Check if number section contains letters that should be numbers
                # Include all O variants (Ø, ø, ∅, ⦸) and lowercase
                number_letters = set('OQILSZBGJ0123456789Øø∅⦸oqilszbgj')
                if all(c in number_letters for c in potential_number_clean) and len(potential_number_clean) <= 4:
                    # Correct the number section
                    corrected_number = self.correct_number(potential_number_clean)
                    if corrected_number.isdigit() and 1 <= len(corrected_number) <= 4:
                        return {
                            'region': potential_region,
                            'number': corrected_number,
                            'series': potential_series,
                            'original': text,
                            'pre_corrected': True
                        }

        return None

    def correct_region(self, region: str) -> str:
        """
        Koreksi huruf wilayah.

        Args:
            region: Huruf wilayah (1-2 karakter)

        Returns:
            Region yang sudah dikoreksi
        """
        # Pastikan uppercase
        region = region.upper()

        # Jika tidak valid, coba koreksi
        if region not in self.valid_region_codes:
            # Coba koreksi karakter yang membingungkan
            corrected = region
            for wrong, correct in self.confusing_chars.items():
                if wrong in region and correct.isalpha():
                    # Hanya ganti jika hasilnya huruf
                    test = region.replace(wrong, correct)
                    if test in self.valid_region_codes:
                        corrected = test
                        break
            return corrected

        return region

    def correct_number(self, number: str) -> str:
        """
        Koreksi bagian angka.
        Ganti huruf yang mirip angka menjadi angka.

        Args:
            number: Bagian angka (1-4 digit)

        Returns:
            Number yang sudah dikoreksi
        """
        corrected = number

        # Mapping huruf → angka (untuk bagian angka)
        letter_to_digit = {
            # O variants (all → 0)
            'O': '0',  # Huruf O → Angka 0
            'o': '0',  # Huruf o (lowercase) → Angka 0
            'Ø': '0',  # O dengan garis miring kanan (U+00D8) → Angka 0
            'ø': '0',  # o dengan garis miring kanan (U+00F8) → Angka 0
            '∅': '0',  # Simbol Empty Set (U+2205) → Angka 0
            '⦸': '0',  # Circled Vertical Stroke (U+29B8) → Angka 0
            'Q': '0',  # Huruf Q → Angka 0
            'q': '0',  # Huruf q → Angka 0
            
            # B/8 variants
            'B': '8',  # Huruf B → Angka 8
            'b': '8',  # Huruf b → Angka 8
            
            # I/1 variants
            'I': '1',  # Huruf I → Angka 1
            'i': '1',  # Huruf i → Angka 1
            'l': '1',  # Huruf l (lowercase L) → Angka 1
            'L': '1',  # Huruf L (capital) → Angka 1 (kadang tertukar)
            
            # S/5 variants
            'S': '5',  # Huruf S → Angka 5
            's': '5',  # Huruf s → Angka 5
            
            # Z/2 variants
            'Z': '2',  # Huruf Z → Angka 2
            'z': '2',  # Huruf z → Angka 2
            
            # G/6 variants
            'G': '6',  # Huruf G → Angka 6
            'g': '6',  # Huruf g → Angka 6
            
            # J/9 variants
            'J': '9',  # Huruf J → Angka 9
            'j': '9',  # Huruf j → Angka 9
        }

        # Replace each character
        result = []
        for char in corrected:
            if char in letter_to_digit:
                result.append(letter_to_digit[char])
            elif char.isdigit():
                result.append(char)
            # Skip non-digit, non-confusing chars

        corrected = ''.join(result)

        # Hapus leading zeros (kecuali hanya "0")
        if corrected and len(corrected) > 1:
            corrected = corrected.lstrip('0') or '0'

        return corrected if corrected else number

    def correct_series(self, series: str) -> str:
        """
        Koreksi huruf seri.
        Ganti angka yang mirip huruf menjadi huruf.

        Args:
            series: Huruf seri (0-3 karakter)

        Returns:
            Series yang sudah dikoreksi
        """
        if not series:
            return series

        corrected = series.upper()

        # Mapping angka → huruf (untuk bagian huruf/seri)
        digit_to_letter = {
            '0': 'O',  # Angka 0 → Huruf O
            '8': 'B',  # Angka 8 → Huruf B
            '1': 'I',  # Angka 1 → Huruf I
            '5': 'S',  # Angka 5 → Huruf S
            '2': 'Z',  # Angka 2 → Huruf Z
            '6': 'G',  # Angka 6 → Huruf G
            '9': 'Q',  # Angka 9 → Huruf Q
        }

        # Karakter khusus yang LANGSUNG jadi O (tidak perlu mapping)
        # Support semua variasi O dengan garis miring (kanan & kiri)
        special_o_chars = {
            'Ø',  # O dengan garis miring kanan (U+00D8)
            'ø',  # o dengan garis miring kanan (U+00F8)
            '∅',  # Empty Set (U+2205)
            '⦸',  # Circled Vertical Stroke (U+29B8)
        }
        
        # Lowercase variants yang langsung jadi uppercase O
        lowercase_to_uppercase = {
            'o': 'O',  # o → O
            'q': 'Q',  # q → Q (nanti akan di-handle di invalid chars)
        }

        # Replace each character
        result = []
        for char in corrected:
            # Check special O characters first (all variants → O)
            if char in special_o_chars:
                result.append('O')
            elif char in lowercase_to_uppercase:
                result.append(lowercase_to_uppercase[char])
            elif char in digit_to_letter:
                result.append(digit_to_letter[char])
            elif char.isalpha():
                # Keep alphabetic chars, but uppercase them
                result.append(char.upper())
            # Skip non-alpha, non-confusing chars

        corrected = ''.join(result)

        # Huruf yang TIDAK boleh ada di seri (I dan Q biasanya tidak digunakan)
        # Tapi kita biarkan karena sudah ada di input
        invalid_chars = {'I', 'Q'}
        for invalid in invalid_chars:
            if invalid in corrected:
                # Ganti dengan huruf yang mirip
                if invalid == 'I':
                    corrected = corrected.replace(invalid, 'L')  # I → L
                elif invalid == 'Q':
                    corrected = corrected.replace(invalid, 'O')  # Q → O

        return corrected if corrected else series

    def validate_plate(self, parsed: Dict[str, str]) -> Tuple[bool, str]:
        """
        Validasi plat nomor.

        Args:
            parsed: Dictionary hasil parse

        Returns:
            (is_valid, message)
        """
        if not parsed:
            return False, "Cannot parse plate format"

        region = parsed.get('region', '')
        number = parsed.get('number', '')
        series = parsed.get('series', '')

        # Validasi region
        if not region or len(region) > 2:
            return False, f"Invalid region code: {region}"

        # Validasi number
        if not number or len(number) > 4:
            return False, f"Invalid number: {number}"

        # Validasi series (optional, bisa 0-3 huruf)
        if series and len(series) > 3:
            return False, f"Invalid series: {series}"

        return True, "Valid plate format"

    def process(self, text: str) -> Dict[str, str]:
        """
        Proses teks hasil OCR dengan validasi dan koreksi.

        Args:
            text: Teks hasil deteksi OCR

        Returns:
            Dictionary dengan hasil processing
        """
        original_text = text.strip().upper()

        # Parse teks
        parsed = self.parse_plate(original_text)

        if not parsed:
            # Format tidak sesuai, kembalikan asli
            return {
                'original': original_text,
                'corrected': original_text,
                'formatted': original_text,
                'is_valid': False,
                'message': 'Format tidak sesuai standar plat nomor Indonesia',
                'components': None
            }

        # Validasi
        is_valid, message = self.validate_plate(parsed)

        if not is_valid:
            # Tidak valid, kembalikan asli
            return {
                'original': original_text,
                'corrected': original_text,
                'formatted': original_text,
                'is_valid': False,
                'message': message,
                'components': parsed
            }

        # Koreksi masing-masing bagian
        corrected_region = self.correct_region(parsed['region'])
        corrected_number = self.correct_number(parsed['number'])
        corrected_series = self.correct_series(parsed['series'])

        # Format hasil
        if corrected_series:
            corrected_text = f"{corrected_region} {corrected_number} {corrected_series}"
            formatted_text = f"{corrected_region} {corrected_number} {corrected_series}"
        else:
            corrected_text = f"{corrected_region} {corrected_number}"
            formatted_text = f"{corrected_region} {corrected_number}"

        return {
            'original': original_text,
            'corrected': corrected_text,
            'formatted': formatted_text,
            'is_valid': True,
            'message': message,
            'components': {
                'region': corrected_region,
                'number': corrected_number,
                'series': corrected_series
            }
        }

    def process_batch(self, texts: List[str]) -> List[Dict[str, str]]:
        """
        Proses multiple teks.

        Args:
            texts: List teks hasil OCR

        Returns:
            List hasil processing
        """
        results = []
        for text in texts:
            result = self.process(text)
            results.append(result)
        return results


# Singleton instance
_processor = None


def get_processor() -> IndonesianPlateProcessor:
    """Get singleton processor instance."""
    global _processor
    if _processor is None:
        _processor = IndonesianPlateProcessor()
    return _processor


def process_plate_text(text: str) -> Dict[str, str]:
    """
    Process single plate text.

    Args:
        text: Teks hasil OCR

    Returns:
        Dictionary hasil processing
    """
    return get_processor().process(text)


def process_plate_batch(texts: List[str]) -> List[Dict[str, str]]:
    """
    Process batch plate texts.

    Args:
        texts: List teks hasil OCR

    Returns:
        List hasil processing
    """
    return get_processor().process_batch(texts)


if __name__ == "__main__":
    # Test cases
    processor = IndonesianPlateProcessor()

    test_cases = [
        # Standard formats
        ("B 1234 CD", "Valid standard"),
        ("BK 987 AB", "Valid 2-letter region"),
        ("D 12 A", "Valid short"),
        ("B 1234", "No series"),
        
        # Without spaces (common OCR result)
        ("B1234CD", "No spaces standard"),
        ("BK987AB", "No spaces 2-letter"),
        ("D12A", "No spaces short"),
        ("B1234", "No spaces no series"),
        
        # OCR errors - letters in number section
        ("B O123 CD", "O should be 0 in number"),
        ("BO123CD", "O should be 0 in number (no space)"),
        ("B I234 CD", "I should be 1 in number"),
        ("BI234CD", "I should be 1 in number (no space)"),
        ("B S678 CD", "S should be 5 in number"),
        ("B Z901 CD", "Z should be 2 in number"),
        
        # Special O characters (Ø - O dengan garis miring)
        ("B Ø123 CD", "Ø should be 0 in number"),
        ("BØ123CD", "Ø should be 0 in number (no space)"),
        ("B 1234 Ø", "Ø should be O in series"),
        ("B1234Ø", "Ø should be O in series (no space)"),
        ("B ∅123 CD", "∅ should be 0 in number"),
        ("B 1234 ⦸", "⦸ should be O in series"),
        
        # OCR errors - numbers in series section
        ("B 1234 0B", "0B should be OB in series"),
        ("B12340B", "0B should be OB in series (no space)"),
        ("B 1234 8", "8 should be B in series"),
        ("B12348", "8 should be B in series (no space)"),
        
        # Invalid series chars (I and Q)
        ("B 1234 I", "I in series (invalid, change to L)"),
        ("B 1234 IQ", "IQ in series (invalid, change to LO)"),
        
        # Invalid formats
        ("BLURRY TEXT", "Invalid - not a plate"),
        ("12345", "Invalid - just numbers"),
        ("ABCDE", "Invalid - just letters"),
    ]

    print("="*70)
    print("Indonesian Plate Processor - Test Results")
    print("="*70)

    for test_input, description in test_cases:
        result = processor.process(test_input)
        print(f"\nInput:    '{test_input}'")
        print(f"          ({description})")
        print(f"Output:   '{result['corrected']}'")
        print(f"Valid:    {'YES' if result['is_valid'] else 'NO'}")
        if not result['is_valid']:
            print(f"Message:  {result['message']}")
        elif result['components']:
            print(f"  Region: {result['components'].get('region', 'N/A')}")
            print(f"  Number: {result['components'].get('number', 'N/A')}")
            print(f"  Series: {result['components'].get('series', 'N/A')}")
