SAMPLES_PKS = {
    'a': """\
        pks_0 a1-a                A1 A2 B1 C1 C2 D1 E1 P1
        """,
    'b': """\
        pks_0 a1-a                B1 C1 C2 D1 E1
              a1-b                B1 C1 C2 D1 E1
        """,
    'c': """\
        pks_0 a1-a                C1 C2 D1
              a1-b                C1 C2 D1
              a1-c                C1 C2 D1
        """,
    'd': """\
        pks_0 a1-a                D1
              a1-b                D1
              a1-c                D1
              a1-d                D1
        """,
    'e': """\
        pks_0 a1-a                E1
              a1-b                E1
              a1-e                E1
        """,
    'f': """\
        pks_0 a1-a                A1 D1
              a1-f                F1 F2 F3 F4
        """,
    'g': """\
        pks_0 a1-a                D1
              a1-b                D1
              a1-c                D1
              a1-d                D1
              a1-g                G1
       """,
    'p': """\
        pks_0 a1-p                A1 A2 B1 C1 C2 D1 E1 P1
        """,
    'o': """\
        pks_0 a1-a                C1 C2 D1
              a1-b                C1 C2 D1
              a1-c                C1 C2 D1
              a1-o                O1 O2 O3 O4 O5
        """,
    'm': """\
        pks_0 a1-m                M1 M2 M3 M4 M5
        """,
    'm_d': """\
        pks_0 a1-a                D1
              a1-b                D1
              a1-c                D1
              a1-d                D1
              a1-m                M3 M4
              a1-m_d              1 2
        """,
    'm_s': """\
        pks_0 a1-m                M1 M2 M3 M4 M5
              a1-m_s              1 2 3 4 5 6 7 8 9
        """,
    'a_some': """\
        pks_0 a1-a                A2 D1
        """,
    'a_some_a_b': """\
        pks_0 a1-a                A2 D1
        new_0 a1-b  .pk           A2 D1
        """,
    'f_a_d': """\
        pks_0 a1-a                A1 D1
              a1-f                F1 F2 F3 F4
        """,
    'd_a_f': """\
        pks_0 a1-a                D1
              a1-b                D1
              a1-c                D1
              a1-d                D1
        new_0 a1-f  .a            D1
        """,
    'o_one_o_s': """\
        pks_0 a1-a                D1
              a1-b                D1
              a1-c                D1
              a1-o                O4
        new_0 a1-o  .pk           O3
        pks_1 a1-a                C2 D1
              a1-b                C2 D1
              a1-c                C2 D1
              a1-o                O1 O3 O4
        """,
    'm_one_m_s': """\
        pks_0 a1-m                M5
        new_0 a1-m_s.to_m         M5
        pks_1 a1-m                M3 M4 M5
              a1-m_s              3 4 5 6 7 8 9
        """,
    'd_d_m': """\
        pks_0 a1-a                D1
              a1-b                D1
              a1-c                D1
              a1-d                D1
        new_0 a1-m_d.d            D1
        pks_1 a1-a                D1
              a1-b                D1
              a1-c                D1
              a1-d                D1
              a1-m                M3 M4
              a1-m_d              1 2
        """,
    'd_d_m_m_s': """\
        pks_0 a1-a                D1
              a1-b                D1
              a1-c                D1
              a1-d                D1
        new_0 a1-m_d.d            D1
        pks_1 a1-a                D1
              a1-b                D1
              a1-c                D1
              a1-d                D1
              a1-m                M3 M4
              a1-m_d              1 2
        new_1 a1-m_s.to_m         M3 M4
        pks_2 a1-a                D1
              a1-b                D1
              a1-c                D1
              a1-d                D1
              a1-m                M3 M4 M5
              a1-m_d              1 2
              a1-m_s              3 4 5 6 7 8 9
        """,
}
