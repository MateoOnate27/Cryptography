PLAIN = bytes.fromhex('00112233445566778899aabbccddeeff')
FIPS_VECTORS = (
    (bytes(range(16)), '69c4e0d86a7b0430d8cdb78070b4c55a'),
    (bytes(range(24)), 'dda97ca4864cdfe06eaf70a0ec0d7191'),
    (bytes(range(32)), '8ea2b7ca516745bfeafc49904b496089'),
)

NIST_PLAIN = bytes.fromhex(
    '6bc1bee22e409f96e93d7e117393172a'
    'ae2d8a571e03ac9c9eb76fac45af8e51'
    '30c81c46a35ce411e5fbc1191a0a52ef'
    'f69f2445df4f9b17ad2b417be66c3710'
)
NIST_VECTORS = (
    ('2b7e151628aed2a6abf7158809cf4f3c',
     '3ad77bb40d7a3660a89ecaf32466ef97'
     'f5d3d58503b9699de785895a96fdbaaf'
     '43b1cd7f598ece23881b00e3ed030688'
     '7b0c785e27e8ad3f8223207104725dd4'),
    ('8e73b0f7da0e6452c810f32b809079e562f8ead2522c6b7b',
     'bd334f1d6e45f25ff712a214571fa5cc'
     '974104846d0ad3ad7734ecb3ecee4eef'
     'ef7afd2270e2e60adce0ba2face6444e'
     '9a4b41ba738d6c72fb16691603c18e0e'),
    ('603deb1015ca71be2b73aef0857d77811f352c073b6108d72d9810a30914dff4',
     'f3eed1bdb5d2a03c064b5a7e3db181f8'
     '591ccb10d410ed26dc5ba74a31362870'
     'b6ed21b99ca6f4f9f153e7b1beafed1d'
     '23304b7a39f9f3ff067d8d8f9e24ecc7'),
)

KEY_CHECKPOINTS = (
    (NIST_VECTORS[0][0], {4:'a0fafe17', 7:'2a6c7605', 40:'d014f9a8',
                          41:'c9ee2589', 42:'e13f0cc8', 43:'b6630ca6'}),
    (NIST_VECTORS[1][0], {6:'fe0c91f7', 8:'ec12068e', 48:'e98ba06f',
                          49:'448c773c', 50:'8ecc7204', 51:'01002202'}),
    (NIST_VECTORS[2][0], {8:'9ba35411', 12:'a8b09c1a', 56:'fe4890d1',
                          57:'e6188d0b', 58:'046df344', 59:'706c631e'}),
)
