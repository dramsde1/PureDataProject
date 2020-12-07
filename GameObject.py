import pygame
import time
import random
import sys
import textwrap
from pythonosc.dispatcher import Dispatcher
from typing import List, Any
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient


class Game:
    def __init__(self):
        self.w = 750
        self.h = 500
        self.reset = True
        self.active = False
        self.input_text = ''
        self.word = ''
        self.time_start = 0
        self.total_time = 0
        self.accuracy = '0%'
        self.results = 'Time:0 Accuracy:0 % Wpm:0 '
        self.wpm = 0
        self.end = False
        self.HEAD_C = (255, 213, 102)
        self.TEXT_C = (240, 240, 240)
        self.RESULT_C = (255, 70, 70)
        self.textvars = {'large':[90,22,90], 'medium':[50,43,45], 'normal':[25,88,20], 'small':[15,148,10]}
        self.place = -1

        pygame.init()
        self.open_img = pygame.image.load('itatchiOpening.jpg')
        self.open_img = pygame.transform.scale(self.open_img, (self.w, self.h))

        self.bg = pygame.image.load('sharingan.jpg')
        self.bg = pygame.transform.scale(self.bg, (750, 630))
        self.screen = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Type Speed test')

   
    def draw_text(self, screen, msg, y, fsize, color):
        font = pygame.font.SysFont('segoeprint', fsize)
        msg = textwrap.fill(msg, self.w)
        text = font.render(msg, 1, color)
        text_rect = text.get_rect(center=(self.w/2, y))
        screen.blit(text, text_rect)
        pygame.display.update()

    def get_sentence(self):
        f = open('sentences.txt').read()
        sentences = f.split('\n')
        sentence = random.choice(sentences)
        return sentence

    def send_music(self, input):
        client = SimpleUDPClient("127.0.0.1", 5005)
        client.send_message("/typing", input)

    def check_progress(self, place, letter):
        if len(self.word) < place:
            return 0
        if self.word[place] == letter:
            self.send_music(1)
            return 1
        else:
            self.send_music(0)
            return 0


    def show_results(self, screen):
        if(not self.end):
            #Calculate time
            self.total_time = time.time() - self.time_start

            #Calculate accuracy
            count = 0
            for i, c in enumerate(self.word):
                try:
                    if self.input_text[i] == c:
                        count += 1
                except:
                    pass
            self.accuracy = count/len(self.word)*100

            #Calculate words per minute
            self.wpm = len(self.input_text)*60/(5*self.total_time)
            self.end = True
            print(self.total_time)

            self.results = 'Time:'+str(round(self.total_time)) + " secs Accuracy:" + str(
                round(self.accuracy)) + "%" + ' Wpm: ' + str(round(self.wpm))

            # draw icon image
            #self.time_img = pygame.image.load('icon.png')
            #self.time_img = pygame.transform.scale(self.time_img, (150, 130))
            #screen.blit(self.time_img, (80,320))
            #screen.blit(self.time_img, (self.w/2-75, self.h-140))
            self.draw_text(screen, "Reset", self.h - 70, 26, (100, 100, 100))

            print(self.results)
            pygame.display.update()

    def run(self):
        self.begin_game()
        self.place = -1
        self.running = True
        while(self.running):
            clock = pygame.time.Clock()
            self.screen.fill((0, 0, 0), (50, 250, 650, 50))
            pygame.draw.rect(self.screen, self.HEAD_C, (50, 250, 650, 50), 1)
            # update the text of user input
            self.draw_text(self.screen, self.input_text,
                           274, 13, (250, 250, 250))
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    #added below 3 lines
                    pygame.display.quit()
                    pygame.quit()
                    quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONUP:
                    x, y = pygame.mouse.get_pos()
                    # position of input box
                    if(x >= 50 and x <= 650 and y >= 250 and y <= 300):
                        self.active = True
                        self.input_text = ''
                        self.place = -1
                        self.time_start = time.time()
                    # position of reset box
                    if(x >= 310 and x <= 510 and y >= 390 and self.end):
                        self.reset_game()
                        x, y = pygame.mouse.get_pos()

                elif event.type == pygame.KEYDOWN:
                    if self.active and not self.end:
                        if event.key == pygame.K_RETURN:
                            print(self.input_text)
                            self.show_results(self.screen)
                            print(self.results)
                            self.draw_text(
                                self.screen, self.results, 350, 28, self.RESULT_C)
                            self.end = True

                        elif event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                            if self.place > -1:
                                self.place -= 1

                        else:
                            try:
                                self.input_text += event.unicode
                                #make sure its not a shift press
                                if event.key != pygame.K_RSHIFT and event.key != pygame.K_LSHIFT:
                                    self.place += 1
                                    self.check_progress(self.place, event.unicode)
                            except:
                                pass

            pygame.display.update()

        clock.tick(60)

    def begin_game(self):
        self.screen.blit(self.open_img, (0, 0))

        pygame.display.update()
        time.sleep(1)

        self.reset = False
        self.end = False
        self.place = -1
        self.input_text = ''
        self.word = ''
        self.time_start = 0
        self.total_time = 0
        self.wpm = 0

        # Get random sentence
        self.word = self.get_sentence()
        if (not self.word):
            self.reset_game()
        #drawing heading
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.bg, (0, -150))
        #msg = "Typing Speed Test"
        #self.draw_text(self.screen, msg, 80, 80, self.HEAD_C)
        # draw the rectangle for input box
        pygame.draw.rect(self.screen, (139, 0, 0), (50, 250, 650, 50), 1)

        # draw the sentence string
        self.draw_text(self.screen, self.word, 200, 16, self.TEXT_C)

        pygame.display.update()

    def reset_game(self):

        self.reset = False
        self.end = False

        self.place = -1
        self.input_text = ''
        self.word = ''
        self.time_start = 0
        self.total_time = 0
        self.wpm = 0

        # Get random sentence
        self.word = self.get_sentence()
        if (not self.word):
            self.reset_game()
        #drawing heading
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.bg, (0, -150))
        #msg = "Typing Speed Test"
        #self.draw_text(self.screen, msg, 80, 80, self.HEAD_C)
        # draw the rectangle for input box
        pygame.draw.rect(self.screen, (139, 0, 0), (50, 250, 650, 50), 1)

        # draw the sentence string
        self.draw_text(self.screen, self.word, 200, 16, self.TEXT_C)

        pygame.display.update()