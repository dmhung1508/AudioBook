from vietvoicetts import synthesize

# Female voice with northern accent and happy emotion
duration = synthesize(
    input(),
    "welcome.wav",
    gender="female",
    area="northern",
    group ="audiobook"
)