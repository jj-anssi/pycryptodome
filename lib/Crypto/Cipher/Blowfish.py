# -*- coding: utf-8 -*-
#
#  Cipher/Blowfish.py : Blowfish
#
# ===================================================================
# The contents of this file are dedicated to the public domain.  To
# the extent that dedication to the public domain is not available,
# everyone is granted a worldwide, perpetual, royalty-free,
# non-exclusive license to exercise all rights associated with the
# contents of this file for any purpose whatsoever.
# No rights are reserved.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ===================================================================
"""
Module's constants for the modes of operation supported with Blowfish:

:var MODE_ECB: Electronic Code Book (ECB)
:var MODE_CBC: Cipher-Block Chaining (CBC)
:var MODE_CFB: Cipher FeedBack (CFB)
:var MODE_OFB: Output FeedBack (OFB)
:var MODE_CTR: CounTer Mode (CTR)
:var MODE_OPENPGP:  OpenPGP Mode
:var MODE_EAX: EAX Mode
"""

import sys

from Crypto.Cipher import _create_cipher
from Crypto.Util._raw_api import (load_pycryptodome_raw_lib,
                                  VoidPointer, SmartPointer, c_size_t,
                                  c_char_ptr)

_raw_blowfish_lib = load_pycryptodome_raw_lib(
        "Crypto.Cipher._raw_blowfish",
        """
        int Blowfish_start_operation(const uint8_t key[],
                                     size_t key_len,
                                     void **pResult);
        int Blowfish_encrypt(const void *state,
                             const uint8_t *in,
                             uint8_t *out,
                             size_t data_len);
        int Blowfish_decrypt(const void *state,
                             const uint8_t *in,
                             uint8_t *out,
                             size_t data_len);
        int Blowfish_stop_operation(void *state);
        """
        )


def _create_base_cipher(dict_parameters):
    """This method instantiates and returns a smart pointer to
    a low-level base cipher. It will absorb named parameters in
    the process."""

    try:
        key = dict_parameters.pop("key")
    except KeyError:
        raise TypeError("Missing 'key' parameter")

    if len(key) not in key_size:
        raise ValueError("Incorrect Blowfish key length (%d bytes)" % len(key))

    start_operation = _raw_blowfish_lib.Blowfish_start_operation
    stop_operation = _raw_blowfish_lib.Blowfish_stop_operation

    void_p = VoidPointer()
    result = start_operation(c_char_ptr(key),
                             c_size_t(len(key)),
                             void_p.address_of())
    if result:
        raise ValueError("Error %X while instantiating the Blowfish cipher"
                         % result)
    return SmartPointer(void_p.get(), stop_operation)


def new(key, mode, *args, **kwargs):
    """Create a new Blowfish cipher

    :param key:
        The secret key to use in the symmetric cipher.
        Its length can vary from 5 to 56 bytes.
    :type key: byte string

    :param mode:
        The chaining mode to use for encryption or decryption.
    :type mode: One of the supported ``MODE_*`` constants

    :Keyword Arguments:
        *   *iv* (``byte string``) --
            (Only applicable for ``MODE_CBC``, ``MODE_CFB``, ``MODE_OFB``,
            and ``MODE_OPENPGP`` modes).

            The initialization vector to use for encryption or decryption.

            For ``MODE_CBC``, ``MODE_CFB``, and ``MODE_OFB`` it must be 8 bytes long.

            For ``MODE_OPENPGP`` mode only,
            it must be 8 bytes long for encryption
            and 10 bytes for decryption (in the latter case, it is
            actually the *encrypted* IV which was prefixed to the ciphertext).

            If not provided, a random byte string is generated (you must then
            read its value with the :attr:`iv` attribute).

        *   *nonce* (``byte string``) --
            (Only applicable for ``MODE_EAX`` and ``MODE_CTR``).

            A value that must never be reused for any other encryption done
            with this key.

            For ``MODE_EAX`` there are no
            restrictions on its length (recommended: **16** bytes).

            For ``MODE_CTR``, its length must be in the range **[0..7]**.

            If not provided for ``MODE_EAX``, a random byte string is generated (you
            can read it back via the ``nonce`` attribute).

        *   *segment_size* (``integer``) --
            (Only ``MODE_CFB``).The number of **bits** the plaintext and ciphertext
            are segmented in. It must be a multiple of 8.
            If not specified, it will be assumed to be 8.

        *   *mac_len* : (``integer``) --
            (Only ``MODE_EAX``)
            Length of the authentication tag, in bytes.
            It must be no longer than 8 (default).

        *   *initial_value* : (``integer``) --
            (Only ``MODE_CTR``). The initial value for the counter within
            the counter block. By default it is **0**.

    :Return: a Blowfish object, of the applicable mode.
    """

    return _create_cipher(sys.modules[__name__], key, mode, *args, **kwargs)

MODE_ECB = 1
MODE_CBC = 2
MODE_CFB = 3
MODE_OFB = 5
MODE_CTR = 6
MODE_OPENPGP = 7
MODE_EAX = 9

# Size of a data block (in bytes)
block_size = 8
# Size of a key (in bytes)
key_size = xrange(5, 56 + 1)
