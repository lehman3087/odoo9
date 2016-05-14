import random

def random_str(randomlength=8):
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.SystemRandom().choice(chars) for i in xrange(randomlength))




def random_num(randomlength=4):
    chars = '0123456789'
    return ''.join(random.SystemRandom().choice(chars) for i in xrange(randomlength))