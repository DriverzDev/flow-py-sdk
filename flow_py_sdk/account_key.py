from __future__ import annotations
from typing import Optional
from ecdsa import SigningKey
from ecdsa.util import randrange_from_seed__trytryagain

import rlp

from flow_py_sdk.frlp import rlp_encode_uint64
from flow_py_sdk.proto.flow import entities
from flow_py_sdk.signer import SignAlgo, HashAlgo, in_memory_signer



class AccountKey(object):
    """
    Flow uses ECDSA to control access to user accounts. Each key pair can be used 
    in combination with the SHA2-256 or SHA3-256 hashing algorithms.
    Here's how to generate an ECDSA private key for the P-256 (secp256r1) curve:

    Parameters
    ----------
    public_key : 
        which is use for verifying a sign.
    sign_algo : int
        Signature algorithm associate with account.
    hash_algo : str
        Hash algorithm associate with account.
    weight:
        Each account key has a weight that determines the signing power it holds.

    """
    weight_threshold: int = 1000

    def __init__(
        self,
        *,
        public_key: bytes,
        sign_algo: SignAlgo,
        hash_algo: HashAlgo,
        weight: Optional[int] = None
    ) -> None:
        super().__init__()
        self.index: Optional[int] = None
        self.public_key: bytes = public_key
        self.sign_algo: SignAlgo = sign_algo
        self.hash_algo: HashAlgo = hash_algo
        self.weight: int = weight if weight is not None else self.weight_threshold
        self.sequence_number: Optional[int] = None
        self.revoked: Optional[bool] = None

    def rlp(self) -> bytes:
        return rlp.encode(
            [
                self.public_key,
                rlp_encode_uint64(self.sign_algo.value),
                rlp_encode_uint64(self.hash_algo.value),
                rlp_encode_uint64(self.weight),
            ]
        )

    def hex(self):
        return self.rlp().hex()

    @classmethod
    def from_proto(cls, k: entities.AccountKey) -> AccountKey:
        """
        from_proto provide a way for user to create a AccountKey instance for an existing account using.

        Parameters
        ----------
        k : AccountKey
            of existing account.

        Returns
        -------
        َAccountKey
            Return Account Key contain public and hash algorithm and signature algorithm. 

        """
        ak = AccountKey(
            public_key=k.public_key,
            hash_algo=HashAlgo(k.hash_algo),
            sign_algo=SignAlgo(k.sign_algo),
            weight=k.weight,
        )
        ak.index = k.index
        ak.revoked = k.revoked
        ak.sequence_number = k.sequence_number

        return ak

    @classmethod
    def from_seed(cls, sign_algo: SignAlgo, hash_algo: HashAlgo, seed: str = None ) -> tuple[AccountKey, in_memory_signer.InMemorySigner]:
        """
        from_seed provide a way for user to create a public and private key for an account using, seed string.

        Parameters
        ----------
        sign_algo : int
            Signature algorithm associate with account.
        hash_algo : str
            Hash algorithm associate with account.
        seed : str
            The seed associate with account.

        Returns
        -------
        َAccountKey
            Return Account Key contain public and hash algorithm and signature algorithm. 
            it also create a InMenorSigner, it can be use signing messages and transactions.

        """
        if sign_algo == None:
            sign_algo = SignAlgo.ECDSA_P256
        if hash_algo == None:
            hash_algo = HashAlgo.SHA2_256
        
        # Generate private key using provided Seed.
        if seed == None:
            private_key = SigningKey.generate()
        else:
            secexp = randrange_from_seed__trytryagain(seed, sign_algo.get_signing_curve().order)
            private_key = SigningKey.from_secret_exponent(secexp, curve = sign_algo.get_signing_curve())

        # Extract public Key (verifying Key) of generated private key.
        public_key = private_key.get_verifying_key()

        #Create Account Key.
        ak = AccountKey(
            public_key = public_key,
            hash_algo = hash_algo,
            sign_algo = sign_algo
        )

        # Save generated private key in in_memory_signer for further messages or transaction Signing.

        signer = in_memory_signer.InMemorySigner(hash_algo =  hash_algo,
        sign_algo = sign_algo,
        private_key_hex = private_key.to_string().hex())

        return ak, signer
