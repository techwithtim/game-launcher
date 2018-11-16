import pygame,os,pygame.gfxdraw,sys,os.path,textwrap
from random import randint,randrange
from .loading_screen import buffer,session_var,user_login
from .leaderboard import Leaderboard
from .server_data import *

#centers launcher to the middle
os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
screen = pygame.display.set_mode((1280,720),pygame.NOFRAME)

buffer(screen,0,0,'AUTHENTICATING...',200).draw(screen)
pygame.display.flip()

DGREY = (60,60,60)
SGREY = (70,70,70)
DDGREY = (40,40,40)
DDDGREY = (35,35,35)
RED = (163, 27, 27)
GREEN = (6, 114, 15)
WHITE = (255,255,255)
DWHITE = (200,200,200)
DDWHITE = (150,150,150)
BLUE = (29, 104, 224)


class random_stars(object):
    def __init__(self,x,y,size):
        self.x = x
        self.y = y
        self.size = size
        self.speed = randint(1,10)
        self.opacity = randint(1,size) * 30 + randint(0,15)
        self.surf = pygame.Surface((size,size))
        self.surf.set_alpha(self.opacity)
        self.surf.fill(WHITE)
        
    def draw(self,surface):
        self.opacity += self.speed
        if self.opacity > 255:
            self.speed = randrange(-1,-10,-1)
        elif self.opacity < 0:
            self.speed = randint(1,10)
        surface.blit(self.surf,(self.x,self.y))
        self.surf.set_alpha(self.opacity)

def star_gaze(w,h,size):
    if h < 0:
        return []
    else:
        if w > 0:
            return [random_stars(randint(w-100,w),randint(h-100,h),randint(2,8))] + star_gaze(w-100,h,size)
        else:
            w = screen.get_width()
            return star_gaze(w,h-100,size) + [random_stars(randint(0,w),randint(h-100,h),randint(2,size))]

class surface_object():
    def __init__(self,w,h,x,y,color,alpha=255):
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.real_y = 0
        self.color = color
        self.surface = pygame.Surface((self.w,self.h))
        self.surface = self.surface.convert()
        self.surface.fill(self.color)
        self.surface.set_alpha(alpha)
    def set_color(self,color):
        self.surface.fill(color)

    def on_mouse_hover(self,y=False):
        if y:
            return pygame.Rect(self.x,self.real_y,self.w,self.h).collidepoint(pygame.mouse.get_pos())
        else:
            return pygame.Rect(self.x,self.y,self.w,self.h).collidepoint(pygame.mouse.get_pos())

    def get_width(self):
        return self.w

    def get_height(self):
        return self.h

    def get_rect(self,y):
        return self.surface.get_rect(center=(self.x,self.y+y))

class popup_window_friend():
    def __init__(self):
        self.main_surface = surface_object(320,400,900,23,DGREY)
        self.top_bar = surface_object(self.main_surface.w,self.main_surface.h/6,self.main_surface.x,self.main_surface.y,DDGREY)
        self.brand_text = draw_text('',30,True,WHITE)
        self.current_window = None
        self.game_buttons = button_grouper(self.top_bar,['FRIENDS','REQUESTS'],button
                                           ,frames=[display_buttons('friends',1,self.main_surface.w,self.main_surface.h - self.main_surface.h/6,0,self.main_surface.h/6),display_buttons('requests',1,self.main_surface.w,self.main_surface.h - self.main_surface.h/6,0,self.main_surface.h/6)]
                                           ,pos=(0,round(self.top_bar.h-self.top_bar.h/2)+23)
                                           ,sizes=(0,self.top_bar.h/2),centerx = True)

        
    def draw(self,surface):
        self.main_surface.surface.blit(self.top_bar.surface,(0,3))
        surface.blit(self.main_surface.surface,(self.main_surface.x,self.main_surface.y))
        if self.current_window is not None:
            self.current_window.draw(surface)
        self.game_buttons.draw(surface)
        pygame.draw.rect(surface,DDWHITE,pygame.Rect(self.main_surface.x,self.main_surface.y,self.main_surface.w,self.main_surface.h),2)
    def check_drag(self):
        if pygame.Rect(self.main_surface.x,self.main_surface.y,self.main_surface.w,self.main_surface.h/6).collidepoint(pygame.mouse.get_pos()):
            self.main_surface.x,self.main_surface.y = pygame.mouse.get_pos()[0]+self.main_surface.x,pygame.mouse.get_pos()[1] +self.main_surface.y

class display_buttons():
    def __init__(self,index,types,w,h,x,y):
        self.type = types
        self.scroll_y = 0
        self.index = index
        self.scroll_bar_size = 1
        self.current = 0
        self.w = w
        self.h = h
        self.x = 900
        self.y = 23 + self.h/6
        self.scrolling = False
        self.background = surface_object(self.w,self.h,self.x,self.y,DGREY)
        self.scroll_bar_frame = surface_object(self.w/20,self.h/1.1,self.w - (self.w/20*2),(self.h - self.h/1.1)/2,SGREY)
        self.scroll_bar = surface_object(self.scroll_bar_frame.w,self.scroll_bar_frame.h*self.scroll_bar_size,900+self.w - (self.w/20*2),self.background.y + self.scroll_bar_frame.y+33,WHITE)
        self.accept_buttons = []
        self.decline_buttons = []
        self.exclude=[]
        self.update_buttons()
 
    def draw(self,surface):
        if self.scrolling:
            self.scroll_bar.y = self.background.y + self.scroll_bar_frame.y + self.current -(self.scroll_y - pygame.mouse.get_pos()[1])
        else:
            self.current = self.scroll_bar.y - (self.background.y + self.scroll_bar_frame.y)
        if self.scroll_bar.y < self.background.y + self.scroll_bar_frame.y + 11: 
            self.scroll_bar.y  = self.background.y + self.scroll_bar_frame.y +11
        elif self.scroll_bar.y > self.background.y + self.scroll_bar_frame.y + (self.scroll_bar_frame.h-self.scroll_bar.h)+ 11:
            self.scroll_bar.y  = self.background.y + self.scroll_bar_frame.y + (self.scroll_bar_frame.h-self.scroll_bar.h)+ 11
        self.background.surface.blit(surface_object(self.background.w,self.background.h,900,23,DGREY).surface,(0,0))
        for i,x in enumerate(self.player_buttons):
            x.y = 23+((i)*80+self.background.y + 80) -self.scroll_bar.y
            x.surface.y = 23+((i)*80+self.background.y + 80)- self.scroll_bar.y
            x.draw(self.background.surface,custom=True)
        for i,x in enumerate(self.accept_buttons):
            x.x,x.y = self.x+10 + self.w/1.2 - self.w/3,23+((i+1)*80+self.background.y + (70-45)/2) -self.scroll_bar.y
            x.surface.x,x.surface.y = self.x+10 + self.w/1.2 - self.w/3,33+((i+1)*80+self.background.y + (70-45)/2) -self.scroll_bar.y
            x.draw(self.background.surface,custom = True)
        for i,x in enumerate(self.decline_buttons):
            x.x,x.y = self.x+10 + self.w/1.2-55,23+((i+1)*80+self.background.y + (70-45)/2) -self.scroll_bar.y
            x.surface.x,x.surface.y = self.x+10 + self.w/1.2-55,33+((i+1)*80+self.background.y + (70-45)/2) -self.scroll_bar.y
            x.draw(self.background.surface,custom = True)
        self.background.surface.blit(self.scroll_bar_frame.surface,(self.scroll_bar_frame.x,(self.background.h - self.scroll_bar_frame.h)/2))
        surface.blit(self.background.surface,(self.x,round(self.h/6+33)))
        self.scroll_bar.x = 900+self.w - (self.w/20*2)
        surface.blit(self.scroll_bar.surface,(self.scroll_bar.x,self.scroll_bar.y))
    def update_buttons(self):
        self.player_buttons = []
        self.accept_buttons = []
        self.decline_buttons = []
        for i,x in enumerate(get_table_data(self.index)):
            if self.index == 'requests':
                b1 = ['y',GREEN,'checkmark.png']
                b2 = ['x',RED,'x.png']
            else:
                b1 = ['C',WHITE,'message.png']
                b2 = ['P',WHITE,'profile.png']
            self.accept_buttons.append(button(self.background,b1[0],center='CENTER',bold=True,font_size=20,color = DDDGREY,text_color = b1[1],startpos=(self.x+10 + self.w/1.2 - 45*2,((self.y+((i)*80+10)))/2),size=(45,45),friends = False,outline=False,user=x,image = b1[2]))
            self.decline_buttons.append(button(self.background,b2[0],center='CENTER',bold=True,font_size=20,color = DDDGREY,text_color = b2[1],startpos=(self.x+10 + self.w/1.2 - 45,((self.y+((i)*80+10)))/2),size=(45,45),friends = False,outline=False,user=x,image = b2[2]))
                
            self.player_buttons.append(button(self.background,x,center='LEFT',bold=True,font_size=20
                                              ,color = DDGREY
                                              ,startpos=(self.x+10,self.y+((i)*80+10)),size=(self.w/1.2,70)
                                              ,friends = True))
        self.scroll_bar_size = self.scroll_bar_frame.h / ((len(self.player_buttons))*80+10) 
        if self.scroll_bar_size > 1:
            self.scroll_bar_size = 1
        self.scroll_bar = surface_object(self.scroll_bar_frame.w,self.scroll_bar_frame.h*self.scroll_bar_size,self.w - (self.w/20*2),self.background.y + self.scroll_bar_frame.y,WHITE)

class launcher():
    def __init__(self,screen):
        self.screen = screen
        self.w = self.screen.get_width()
        self.h = self.screen.get_height()
        self.frame_selected = None
        self.game_screen = None
        self.leaderb_menu = None
        self.prevgame_screen = None
        self.fr_menu = None
        self.top_bar = surface_object(self.w,self.h/8,0,0,DDGREY)
        self.enlarge = False
        self.friends_open = False
        self.open_chat_bar = False
        self.chat_windows = []
        self.brand_text = draw_text('TRNT v1.0',30,True,WHITE)

        self.user_text = draw_text('Welcome, ' + user.upper() +'!',17,False,WHITE)
        
        self.home_menu = home_screen(self.screen)
        self.frame_selected = self.home_menu
        self.library_menu = library_screen(self.screen)
        self.stats_menu = stats_screen(self.screen)
        self.profile_menu = profile_screen(self.screen,user_login)
        self.community_menu = community_screen(self.screen)
        self.main_buttons = button_grouper(self.top_bar,['HOME','LIBRARY','PROFILE','COMMUNITY','GLOBAL STATS']
                                           ,button,frames=[self.home_menu,self.library_menu,self.profile_menu,self.community_menu,self.stats_menu],pos=(0,self.top_bar.h/2),sizes=(0,self.top_bar.h/2),centerx = True)
        self.main_buttons.button_list[0].selected = True
        self.close_button = button(self.screen,'x',startpos=(self.top_bar.w-self.top_bar.w/25,0),size=(self.top_bar.w/25,self.top_bar.h/4),text_color=DDWHITE,color=DDGREY,font_size=15,bold = True)
        self.enlarge_button = button(self.screen,'□',startpos=(self.top_bar.w-self.top_bar.w/25-self.top_bar.w/25,0),size=(self.top_bar.w/25,self.top_bar.h/4),text_color=DDWHITE,color=DDGREY,font_size=15,bold = False)
        self.minimize_button = button(self.screen,'-',startpos=(self.top_bar.w-self.top_bar.w/25-self.top_bar.w/25-self.top_bar.w/25,0),size=(self.top_bar.w/25,self.top_bar.h/4),text_color=DDWHITE,color=DDGREY,font_size=16,bold = True)

        self.friends_button = button(self.screen,'FRIENDS',startpos=(self.top_bar.w-(self.top_bar.w/25*4),0)
                                     ,size=(40,40),text_color=DDWHITE,color=DDGREY,font_size=10,bold = True,image = 'friends_icon.png')
        self.chat_bar = None
        ##FRIENDS WINDOW
        self.friends_window = popup_window_friend()
    def draw(self,surface):
        if self.frame_selected is not None:
            self.frame_selected.draw(surface)
            if isinstance(self.frame_selected,library_screen) and self.game_screen is not None:
                self.game_screen.draw(surface)
            if isinstance(self.leaderb_menu,Leaderboard) and self.leaderb_menu is not None and isinstance(self.frame_selected,stats_screen):
                self.leaderb_menu.draw()
            if isinstance(self.frame_selected,profile_screen) and self.fr_menu is not None:
                self.fr_menu.draw(surface)
            
        surface.blit(self.top_bar.surface,(self.top_bar.x,self.top_bar.y))
        self.main_buttons.draw(surface)
        surface.blit(self.brand_text.surface,(10,0))
        surface.blit(self.user_text.surface,(self.top_bar.w - self.user_text.width-(self.top_bar.w/25*5),0))
        self.close_button.draw(surface)
        self.enlarge_button.draw(surface)
        self.minimize_button.draw(surface)
        self.friends_button.draw(surface)
        if self.friends_open:
            self.friends_window.draw(surface)
        if self.open_chat_bar:
            self.chat_bar.draw(surface)
        for x in self.chat_windows:
            x.draw(surface)

    def check_buttons(self):
        if pygame.Rect(self.friends_window.main_surface.x,self.friends_window.main_surface.y,self.friends_window.main_surface.w,self.friends_window.main_surface.h).collidepoint(pygame.mouse.get_pos()) and self.friends_open:
            pass
        else:self.frame_selected = self.main_buttons.check_event(self.frame_selected)
        self.game_screen = self.library_menu.game_buttons.check_event(self.game_screen)
        self.leaderb_menu = self.stats_menu.select_scores.check_event(self.leaderb_menu)
        self.friends_window.current_window = self.friends_window.game_buttons.check_event(self.friends_window.current_window)
        if isinstance(self.frame_selected,community_screen):
            for x in self.community_menu.player_buttons:
                if x.on_mouse_click() and self.community_menu.players_box.on_mouse_hover(y = True):
                    self.open_profile(x.user)
            if self.community_menu.refresh_button.on_mouse_click():
                buffer(self.community_menu.players_box,self.community_menu.players_box.x
                       ,self.community_menu.players_box.y + self.community_menu.display_screen.y,'WAITING').draw(surf = self.screen)
                self.community_menu.update_buttons()
        if isinstance(self.frame_selected,stats_screen):
            if self.stats_menu.refresh_button.on_mouse_click():
                buffer(self.stats_menu.leader_board_display,self.stats_menu.leader_board_display.x,self.stats_menu.leader_board_display.y + self.stats_menu.display_screen.y,'WAITING').draw(surf = self.screen)
                for i in self.stats_menu.select_scores.frames:
                    i.update()
        if isinstance(self.frame_selected,profile_screen):
            self.frame_selected.check_buttons()
            if self.frame_selected.message_button.on_mouse_click():
                self.chat_windows.append(chat_window(self.screen,user_login,self.frame_selected.user))
            if self.frame_selected.back_button.on_mouse_click():
                for x in self.main_buttons.button_list:
                    x.selected = False
                self.main_buttons.button_list[3].selected = True
                self.frame_selected = self.community_menu
        if isinstance(self.frame_selected,library_screen) and self.game_screen is not None:
            game_directory = (os.path.abspath(os.path.join(os.path.dirname(__file__), '../games/'+self.game_screen.name)))
            sys.path.append(game_directory)
            if self.game_screen.name == 'quicktype' and self.game_screen.play_button.on_mouse_click():
                import reactionGame
                reactionGame.start(user_login)
            elif self.game_screen.name == 'integerrecall' and self.game_screen.play_button.on_mouse_click():
                import integerRecall
                integerRecall.start(user_login)
            elif self.game_screen.name == 'golfgame' and self.game_screen.play_button.on_mouse_click():
                pass
        if self.minimize_button.on_mouse_click():
            pygame.display.iconify()
        if self.close_button.on_mouse_click():
            pygame.quit()
            raise SystemExit
        if len(self.chat_windows) != 0:
            for i,x in enumerate(self.chat_windows):
                if x.open:
                    if x.close_button.on_mouse_click():
                        del self.chat_windows[i]
                    if x.send_button.on_mouse_click():
                        x.send_text_message()
                if x.display_screen.on_mouse_hover():
                    x.selected = True
                else:
                    x.selected = False
        if self.friends_button.on_mouse_click():
            for x in self.friends_window.game_buttons.frames:
                x.update_buttons()
            if self.friends_open:
                self.friends_open = False
            else:
                self.friends_open = True
        if self.enlarge_button.on_mouse_click():
            if self.enlarge:
                screen = pygame.display.set_mode((1280,720),pygame.NOFRAME)
                self.enlarge = False
            else:
                #screen = pygame.display.set_mode((1920,1080),pygame.NOFRAME)
                self.enlarge = True
        if self.friends_open:
            if self.friends_window.game_buttons.frames[1] == self.friends_window.current_window and self.friends_window.current_window.background.on_mouse_hover():
                for x in self.friends_window.current_window.accept_buttons:
                    if x.on_mouse_click():
                        accept_friend_request(x.user)
                        self.friends_window.current_window.update_buttons()
                for x in self.friends_window.current_window.decline_buttons:
                    if x.on_mouse_click():
                        decline_friend_request(x.user)
                        self.friends_window.current_window.update_buttons()
            elif self.friends_window.game_buttons.frames[0] == self.friends_window.current_window  and self.friends_window.current_window.background.on_mouse_hover(): 
                for x in self.friends_window.current_window.decline_buttons:
                    if x.on_mouse_click():
                        self.open_profile(x.user)
                for x in self.friends_window.current_window.accept_buttons:
                    if x.on_mouse_click():
                        self.chat_windows.append(chat_window(self.screen,user_login,x.user))
                        
    def open_profile(self,user):
        for x in self.main_buttons.button_list:
            x.selected = False
        self.main_buttons.button_list[2].selected = True
        self.frame_selected = profile_screen(self.screen,user,True)
        
    def check_scroll(self,event):
        if isinstance(self.frame_selected,library_screen):
            for x in self.library_menu.game_buttons.frames:
                if x is not None:
                    if x.scroll_bar.on_mouse_hover():
                        if event == pygame.MOUSEBUTTONDOWN:
                            x.scrolling = True
                            x.scroll_y = pygame.mouse.get_pos()[1]
                        else:
                            x.scrolling = False
                    else:
                        x.scrolling = False
        if isinstance(self.frame_selected,community_screen):
            if self.frame_selected.scroll_bar.on_mouse_hover():
                if event == pygame.MOUSEBUTTONDOWN:
                    self.frame_selected.scrolling = True
                    self.frame_selected.scroll_y = pygame.mouse.get_pos()[1]
                else:
                    self.frame_selected.scrolling = False
            else:
                self.frame_selected.scrolling = False
        if self.friends_open:
            if self.friends_window.game_buttons.frames[0] == self.friends_window.current_window:
                if self.friends_window.current_window.scroll_bar.on_mouse_hover():
                    if event == pygame.MOUSEBUTTONDOWN:
                        self.friends_window.current_window.scrolling = True
                        self.friends_window.current_window.scroll_y = pygame.mouse.get_pos()[1]
                    else:
                        self.friends_window.current_window.scrolling = False
                else:
                    self.friends_window.current_window.scrolling = False
            elif self.friends_window.game_buttons.frames[1] == self.friends_window.current_window:
                if self.friends_window.current_window.scroll_bar.on_mouse_hover():
                    if event == pygame.MOUSEBUTTONDOWN:
                        self.friends_window.current_window.scrolling = True
                        self.friends_window.current_window.scroll_y = pygame.mouse.get_pos()[1]
                    else:
                        self.friends_window.current_window.scrolling = False
                else:
                    self.friends_window.current_window.scrolling = False
        if len(self.chat_windows) != 0:
            for x in self.chat_windows:
                if x.open:
                    if event == pygame.MOUSEBUTTONDOWN:
                        x.scrolling = True
                        x.scroll_y = pygame.mouse.get_pos()[1]
                    else:
                        x.scrolling = False
    def reset_path(self):
        game_directory = (os.path.abspath(os.path.join(os.path.dirname(__file__), '')))
        game_directory = os.path.abspath(os.path.join(game_directory, ''))
        sys.path.append(game_directory)
class main_frame():
    def __init__(self,parent):
        self.parent = parent
        self.w = self.parent.get_width()
        self.h = self.parent.get_height()/8*7
        self.x = self.parent.get_width()/8
        self.y = self.parent.get_height()/8
        self.scroll_y = 0

        self.display_screen = surface_object(self.w,self.h,0,self.y,DGREY)

        self.scroll_bar_frame = surface_object(self.w/70,self.h/1.3,self.x*7.5,(self.h - self.h/1.3)/2,SGREY)

        self.scroll_bar = surface_object(self.scroll_bar_frame.w,50,self.scroll_bar_frame.x+self.display_screen.x+self.scroll_bar_frame.w+2,163,WHITE)
        
    def draw(self,surface):
        surface.blit(self.display_screen.surface,(self.display_screen.x,self.display_screen.y))

class home_screen(main_frame):
    def __init__(self,parent):
        super().__init__(parent)
        self.game_text = draw_text("WELCOME TO THE COMMUNITY",30,True,WHITE)
        self.player_size = 0
        self.news1=self.news2=self.news3 = []
        self.title1=self.title2=self.title3 =self.playerofweek= ''

        self.bg_title = surface_object(self.display_screen.w/1.2,50
                                       ,(self.display_screen.w-self.display_screen.w/1.2)/2,7,DDGREY)

        self.bg_title2 = surface_object(self.display_screen.w/1.7,35
                                       ,(self.display_screen.w-self.display_screen.w/1.2)/2,7,DDGREY)

        self.bg_title3 = surface_object(self.display_screen.w/1.7,35
                                       ,(self.display_screen.w-self.display_screen.w/1.2)/2,7,DDGREY)

        self.section1 = surface_object(300,350
                                       ,150,150,DDGREY)

        self.section2 = surface_object(300,350
                                       ,(self.display_screen.w-300)/2,150,DDGREY)

        self.section3 = surface_object(300,350
                                       ,self.display_screen.w-450,150,DDGREY)

        self.refresh_button = button(self.display_screen,'REFRESH',startpos = ((self.display_screen.w-200)/2
                                                                               ,661),size=(200,50))
        self.get_profile_stats()
        self.par_title1 = draw_text(self.title1,20,True,WHITE)
        self.par_title2 = draw_text(self.title2,20,True,WHITE)
        self.par_title3 = draw_text(self.title3,20,True,WHITE)
        self.game_text2 = draw_text("PLAYER OF THE WEEK: " + self.playerofweek.upper(),21,False,WHITE)
        self.game_text3 = draw_text("COMMUNITY SIZE: " + str(self.player_size),21,False,WHITE)
    def draw(self,surface):
        self.display_screen.surface.blit(self.bg_title.surface
                                         ,((self.display_screen.w-self.display_screen.w/1.2)/2,25))

        self.display_screen.surface.blit(self.bg_title2.surface
                                         ,((self.display_screen.w-self.display_screen.w/1.7)/2,95))

        self.display_screen.surface.blit(self.bg_title3.surface
                                         ,((self.display_screen.w-self.display_screen.w/1.7)/2,520))

        self.display_screen.surface.blit(self.game_text.surface
                                         ,((self.display_screen.w-self.game_text.width)/2,30))
        self.display_screen.surface.blit(self.game_text2.surface
                                         ,((self.display_screen.w-self.game_text2.width)/2,100))
        self.display_screen.surface.blit(self.game_text3.surface
                                         ,((self.display_screen.w-self.game_text3.width)/2,525))

        self.display_screen.surface.blit(self.section1.surface
                                         ,(self.section1.x,self.section1.y))
        self.display_screen.surface.blit(self.section2.surface
                                         ,(self.section2.x,self.section2.y))
        self.display_screen.surface.blit(self.section3.surface
                                         ,(self.section3.x,self.section3.y))

        self.display_screen.surface.blit(self.par_title1.surface
                                         ,(self.section1.x + (self.section1.w-self.par_title1.width)/2,self.section1.y+10))
        self.display_screen.surface.blit(self.par_title2.surface
                                         ,((self.display_screen.w-self.par_title2.width)/2,self.section2.y+10))
        self.display_screen.surface.blit(self.par_title3.surface
                                         ,(self.section3.x + (self.section3.w-self.par_title3.width)/2,self.section3.y+10))

        for i,x in enumerate(self.news1):
            self.display_screen.surface.blit(x.surface,(self.section1.x + 10,x.height*i + 40+ self.section1.y))
        for i,x in enumerate(self.news2):
            self.display_screen.surface.blit(x.surface,(self.section2.x + 10,x.height*i + 40+ self.section2.y))
        for i,x in enumerate(self.news3):
            self.display_screen.surface.blit(x.surface,(self.section3.x + 10,x.height*i + 40 + self.section3.y))
        surface.blit(self.display_screen.surface,(self.display_screen.x,self.display_screen.y))
        
        self.refresh_button.draw(surface)

    def get_profile_stats(self):
        playerofweek=news1=news2=news3 = []
        self.news1=[]
        self.news2=[]
        self.news3 = []
        self.player_size = len(get_players(''))
        playerofweek,news1,news2,news3 = get_launcher_settings()
        self.playerofweek = playerofweek
        self.title1 = news1[0]
        self.title2 = news2[0]
        self.title3 = news3[0]
        for i,x in enumerate(textwrap.wrap(news1[1],width=40)):
            self.news1.append(draw_text(x,15,False,WHITE))
        for z,b in enumerate(textwrap.wrap(news2[1],width=40)):
            self.news2.append(draw_text(b,15,False,WHITE))
        for g,h in enumerate(textwrap.wrap(news3[1],width=40)):
            self.news3.append(draw_text(h,15,False,WHITE))
class chat_window(main_frame):
    def __init__(self,parent,user1,user2):
        super().__init__(parent)
        self.user1 = user1
        self.user2 = user2
        self.chat_text = self.get_chat_text()
        self.text_list = []
        self.font_size = 15
        self.open = True
        self.selected = False
        self.scrolling = False
        self.scroll_y = 0
        self.current = 0
        self.search_text = []
        self.display_screen = surface_object(220,250,(self.parent.get_width()-230)/2,(self.parent.get_height()-300)/2,DGREY,alpha = 230)
        self.scroll_bar_frame = surface_object(self.display_screen.w/20,self.display_screen.h/1.5,self.display_screen.w - self.display_screen.w/20 * 2,(self.display_screen.h - self.display_screen.h/1.5)/2,SGREY)
        self.scroll_bar = surface_object(self.scroll_bar_frame.w,50,self.scroll_bar_frame.x+self.display_screen.x,self.scroll_bar_frame.y + self.display_screen.y,WHITE)
        self.top_bar = surface_object(self.display_screen.w,self.display_screen.h/10,0,0,DDGREY)
        self.bottom_bar = surface_object(self.display_screen.w,self.display_screen.h/7,0,self.display_screen.h-self.display_screen.h/7,DDGREY)
        self.c_text = draw_text('IMS: ' + self.user2.upper(),12,True,WHITE)
        self.close_button = button(self.display_screen,'x',startpos=(self.top_bar.w-self.top_bar.w/8 + self.display_screen.x,self.display_screen.y),size=(self.top_bar.w/8,self.top_bar.h),text_color=RED,color=DDGREY,font_size=15,bold = True)
        self.type_text = draw_text(''.join(self.search_text),12,True,WHITE)
        self.send_button = button(self.display_screen,'SEND',startpos=(self.bottom_bar.w-self.bottom_bar.w/4 + self.display_screen.x,self.display_screen.y + self.display_screen.h -self.bottom_bar.h),size=(self.bottom_bar.w/4,self.bottom_bar.h),text_color=WHITE,color=DDGREY,font_size=17,bold = False)
        self.timer = 0
        self.parse_text()
    def draw(self,surface):
        if self.timer == 100:
            self.timer = 0
            self.chat_text = self.get_chat_text()
            self.parse_text()
        self.timer +=1
        self.type_text = draw_text(''.join(self.search_text),12,True,WHITE)
        if self.scrolling:
            self.scroll_bar.y = (self.display_screen.h-self.scroll_bar_frame.h)/2 + self.display_screen.y + self.current -((self.scroll_y) - pygame.mouse.get_pos()[1])
        else:
            self.current = self.scroll_bar.y - (self.display_screen.y + self.scroll_bar_frame.y)
        if self.scroll_bar.y < self.display_screen.y + self.scroll_bar_frame.y: 
            self.scroll_bar.y  = self.display_screen.y + self.scroll_bar_frame.y
        elif self.scroll_bar.y > self.display_screen.y + self.scroll_bar_frame.y + (self.scroll_bar_frame.h-self.scroll_bar.h):
            self.scroll_bar.y  = self.display_screen.y + self.scroll_bar_frame.y + (self.scroll_bar_frame.h-self.scroll_bar.h)
        self.display_screen.surface.blit(surface_object(self.display_screen.w,self.display_screen.h,0,0,DGREY).surface,(0,0))
        total_size = self.top_bar.h
        for x in self.text_list:
            self.display_screen.surface.blit(x.surface,(10,total_size-(self.scroll_bar.y-(self.display_screen.y + self.scroll_bar_frame.y))))
            total_size += x.height
        
        self.display_screen.surface.blit(self.bottom_bar.surface,(0,self.display_screen.h-self.display_screen.h/7))
        self.display_screen.surface.blit(self.top_bar.surface,(0,0))
        self.display_screen.surface.blit(self.c_text.surface,(10,(self.top_bar.h-self.c_text.height)/2))
        self.display_screen.surface.blit(self.type_text.surface,(10,(self.bottom_bar.h-self.c_text.height)/2+self.bottom_bar.y))
        self.display_screen.surface.blit(self.scroll_bar_frame.surface,(self.scroll_bar_frame.x,self.scroll_bar_frame.y))
        surface.blit(self.display_screen.surface,(self.display_screen.x,self.display_screen.y))
        surface.blit(self.scroll_bar.surface,(self.scroll_bar.x,self.scroll_bar.y))
        self.close_button.draw(surface)
        self.send_button.draw(surface)
        if self.selected:
            pygame.draw.rect(surface,RED,pygame.Rect(self.display_screen.x,self.display_screen.y,self.display_screen.w,self.display_screen.h),3)
        else:
            pygame.draw.rect(surface,DDWHITE,pygame.Rect(self.display_screen.x,self.display_screen.y,self.display_screen.w,self.display_screen.h),2)
    def parse_text(self):
        lens=1
        self.text_list = []
        if self.chat_text is not None:
            for i,x in enumerate(self.chat_text):
                text_color = DDWHITE
                if ''.join(x[0]) == user_login:
                    text_color = WHITE
                for z in textwrap.wrap(''.join(x[0]) + ': ' +''.join(x[1]),width=28):
                    self.text_list.append(draw_text(z,self.font_size,False,text_color))
        for x in self.text_list:
            lens+= x.height
        self.scroll_bar_size = self.scroll_bar_frame.h /  lens
        if self.scroll_bar_size > 1:
            self.scroll_bar_size = 1
        self.scroll_bar = surface_object(self.scroll_bar_frame.w,self.scroll_bar_frame.h*self.scroll_bar_size,self.scroll_bar_frame.x+self.display_screen.x,self.scroll_bar_frame.y + self.display_screen.y,WHITE)
    def get_chat_text(self):
        return get_chat_log(self.user1,self.user2)
    
    def send_text_message(self):
        msg = ''.join(self.search_text)
        if msg != '' and msg != ' ':
            send_message(self.user1,self.user2,msg)
            self.search_text = []
            self.chat_text = self.get_chat_text()
            self.parse_text()

class community_screen(main_frame):
    def __init__(self,parent):
        super().__init__(parent)
        self.search_text = []
        self.player_buttons = []
        self.clicked_player = None
        self.scrolling = False
        self.search_bg = surface_object(self.w/2,50,(self.display_screen.w-self.w/2)/2,self.display_screen.h/20,DDGREY)
        self.text = draw_text('SEARCH:',30,True,WHITE)
        self.players_box = surface_object(self.w/2,self.h/1.2,(self.display_screen.w-self.w/2)/2,self.display_screen.h/7,DDGREY)
        self.players_box.real_y = self.display_screen.h/7 + self.display_screen.y
        self.refresh_button = button(self.display_screen,'FIND',startpos = (self.search_bg.x + self.search_bg.w-105,self.display_screen.h/5),size=(100,40),color=DGREY)
        self.update_buttons()
    def draw(self,surface):
        if self.scrolling:
            self.scroll_bar.y = (self.players_box.h-self.scroll_bar_frame.h)/2 + self.players_box.y + self.display_screen.y + self.current -(self.scroll_y - pygame.mouse.get_pos()[1])
        else:
            self.current = self.scroll_bar.y - (self.players_box.y + self.scroll_bar_frame.y)
        if self.scroll_bar.y < self.players_box.y + self.scroll_bar_frame.y + 39: 
            self.scroll_bar.y  = self.players_box.y + self.scroll_bar_frame.y +39
        elif self.scroll_bar.y > self.players_box.y + self.scroll_bar_frame.y + (self.scroll_bar_frame.h-self.scroll_bar.h)+ 39:
            self.scroll_bar.y  = self.players_box.y + self.scroll_bar_frame.y + (self.scroll_bar_frame.h-self.scroll_bar.h)+ 39
        self.c_text = draw_text(''.join(self.search_text),30,False,WHITE)
        self.players_box.surface.blit(surface_object(self.players_box.w,self.players_box.h,0,0,DDGREY).surface,(0,0))
        for i,x in enumerate(self.player_buttons):
            x.x,x.y=10,210+((i)*110+10)-self.scroll_bar.y
            x.surface.x,x.surface.y=self.players_box.x + 10,self.players_box.y + self.display_screen.y+ 210+((i)*110+10)-self.scroll_bar.y
            x.draw(self.players_box.surface)
        self.players_box.surface.blit(self.scroll_bar_frame.surface,(self.players_box.w/4*3.8,(self.players_box.h-self.scroll_bar_frame.h)/2))
        self.display_screen.surface.blit(self.players_box.surface,(self.players_box.x,self.display_screen.h/7))
        self.display_screen.surface.blit(self.search_bg.surface,(self.search_bg.x,self.search_bg.y))
        surface.blit(self.display_screen.surface,(self.display_screen.x,self.display_screen.y))
        surface.blit(self.text.surface,(self.search_bg.x+10,self.display_screen.h/5))
        surface.blit(self.c_text.surface,(self.search_bg.x+150,self.display_screen.h/5))
        self.refresh_button.draw(surface)
        surface.blit(self.scroll_bar.surface,(self.scroll_bar.x,self.scroll_bar.y))
    def update_buttons(self):
        self.player_buttons = []
        for i,x in enumerate(get_players(''.join(self.search_text))):
            self.player_buttons.append(button(self.players_box.surface,x,center='LEFT',bold=True,font_size=40,color = DGREY
                                              ,startpos=(self.search_bg.x+10,self.display_screen.h/3.5+((i)*110+10)),size=(self.w/2.2,100),user=x))
        self.scroll_bar_size = self.scroll_bar_frame.h /  (210 +(len(self.player_buttons))*280+10)
        if self.scroll_bar_size > 1:
            self.scroll_bar_size = 1
        self.scroll_bar = surface_object(self.scroll_bar_frame.w,self.scroll_bar_frame.h*self.scroll_bar_size,self.players_box.w/4*3.8 + self.players_box.x,self.players_box.y + self.scroll_bar_frame.y + 39,WHITE)


class library_screen(main_frame):
    def __init__(self,parent):
        super().__init__(parent)
        self.side_bar = surface_object(self.display_screen.w/6,self.display_screen.h,0,0,DGREY)
        self.game_buttons = button_grouper(self.side_bar,['QUICKTYPE','INTEGER RECALL','GOLF GAME'],button
                                           ,frames=[game_frame(self.parent,'quicktype','quicktype'),game_frame(self.parent,'integerrecall','integerrecall'),game_frame(self.parent,'golfgame','golf')],pos=(0,self.display_screen.y),sizes=(self.side_bar.w,0),centery = True)
        self.stars  = star_gaze(self.display_screen.w,self.display_screen.h,7)
    def draw(self,surface):
        #self.scroll_bar_frame.surface.blit(self.scroll_bar.surface,(self.scroll_bar_frame.x,self.scroll_bar.y))
        #self.display_screen.surface.blit(self.scroll_bar_frame.surface,(self.scroll_bar_frame.x,(self.display_screen.h - self.scroll_bar_frame.h)/2))
        self.display_screen.surface.blit(self.side_bar.surface,(0,0))
        surface.blit(self.display_screen.surface,(0,self.display_screen.y))
        for x in self.stars:
            x.draw(surface)
        self.game_buttons.draw(surface)
        
class draw_text():
    def __init__(self,text,font_size,bold,color):
        self.text = text
        self.font_size = font_size
        self.bold = bold
        self.color = color
        self.font = pygame.font.SysFont('tahoma',self.font_size,self.bold)
        self.surface = self.font.render(self.text,True,self.color)
        self.width = self.surface.get_width()
        self.height = self.surface.get_height()     
  
class game_frame(main_frame):
    def __init__(self,parent,name,to_run):
        super().__init__(parent)
        self.move_val = 0
        self.name = name
        self.scrolling = False
        self.display_screen = surface_object(self.w-self.w/6,self.h,self.w/6,self.y,DGREY)
        self.display_screen.surface.set_alpha(220)
        self.bg_picture = surface_object(self.display_screen.w/1.2,400,(self.display_screen.w - self.display_screen.w/1.2)/2,100,DDGREY)
        self.bg_leader = surface_object(self.display_screen.w/1.2,400,(self.display_screen.w-self.display_screen.w/1.2)/2,650-(self.scroll_y-163),DDGREY)
        self.bg_title = surface_object(self.display_screen.w/1.2,50,(self.display_screen.w-self.display_screen.w/1.2)/2,10-self.move_val,DDGREY)
        self.game_text = draw_text(name.upper(),40,True,WHITE)

        self.led_bg = surface_object(self.display_screen.w/1.2,50,(self.display_screen.w-self.display_screen.w/1.2)/2,600-self.move_val,DDGREY)
        self.led_text = draw_text('LEADERBOARDS',35,True,WHITE)
        
        self.scroll_bar_frame = surface_object(self.w/70,self.h/1.3,self.x*6.3,(self.display_screen.h - self.scroll_bar_frame.h)/2,SGREY)
        self.play_button = button(self.display_screen,'PLAY',text_color=WHITE,bold=True,font_size=60,startpos = ((self.display_screen.w+self.display_screen.w/15)/2,570-(self.scroll_y-163)),size=(self.display_screen.w/3,80),color=GREEN)
        self.image = pygame.image.load('materials/'+name+'.png')
        self.image = pygame.transform.scale(self.image,(int(self.bg_picture.w),int(self.bg_picture.h+190)))

        self.quicktype_scores = Leaderboard(user,to_run,'friends',parent,self.bg_leader.w,self.bg_leader.h

                                                   ,self.bg_leader.x,self.bg_leader.y,True)
        self.scroll_bar_size = self.scroll_bar_frame.h / 4000
        self.scroll_bar = surface_object(self.scroll_bar_frame.w,self.scroll_bar_frame.h*self.scroll_bar_size,self.display_screen.x + self.scroll_bar_frame.x,self.display_screen.y + self.scroll_bar_frame.y,WHITE)
    def draw(self,surface):
        if self.scrolling:
            self.scroll_bar.y = (self.display_screen.h-self.scroll_bar_frame.h)/2 + self.display_screen.y + self.current -(self.scroll_y - pygame.mouse.get_pos()[1])
        else:
            self.current = self.scroll_bar.y - (self.display_screen.y + self.scroll_bar_frame.y)
        if self.scroll_bar.y < self.display_screen.y + self.scroll_bar_frame.y: 
            self.scroll_bar.y  = self.display_screen.y + self.scroll_bar_frame.y
        elif self.scroll_bar.y > self.display_screen.y + self.scroll_bar_frame.y + (self.scroll_bar_frame.h-self.scroll_bar.h):
            self.scroll_bar.y  = self.display_screen.y + self.scroll_bar_frame.y + (self.scroll_bar_frame.h-self.scroll_bar.h)


        self.display_screen.surface.blit(surface_object(self.display_screen.w,self.display_screen.h,0,0,DGREY).surface,(0,0))
        self.bg_picture.surface.blit(self.image,(0,0))
        self.display_screen.surface.blit(self.bg_picture.surface,(self.bg_picture.x,90-(self.scroll_bar.y-163)))
        self.display_screen.surface.blit(self.bg_title.surface,((self.display_screen.w-self.display_screen.w/1.2)/2,30-(self.scroll_bar.y-163)))
        self.display_screen.surface.blit(self.game_text.surface,((self.display_screen.w-self.game_text.width)/2,30-(self.scroll_bar.y-163)))
        self.display_screen.surface.blit(self.bg_leader.surface,((self.display_screen.w-self.bg_leader.w)/2,650-(self.scroll_bar.y-163)))

        self.display_screen.surface.blit(self.led_bg.surface,((self.display_screen.w-self.display_screen.w/1.2)/2,590-(self.scroll_bar.y-163)))
        self.display_screen.surface.blit(self.led_text.surface,((self.display_screen.w-self.led_text.width)/2,590-(self.scroll_bar.y-163)))
        
        self.display_screen.surface.blit(self.scroll_bar_frame.surface,(self.scroll_bar_frame.x,(self.display_screen.h - self.scroll_bar_frame.h)/2))
        self.play_button.y=self.play_button.surface.y = 590-(self.scroll_bar.y-163)
        self.play_button.draw(self.display_screen.surface,custom=True)
        surface.blit(self.display_screen.surface,(self.display_screen.x,self.display_screen.y))
        self.quicktype_scores.x,self.quicktype_scores.y = (self.display_screen.w-self.bg_leader.w)/2+self.display_screen.x,650-(self.scroll_bar.y-163)+self.display_screen.y
        self.quicktype_scores.draw()
        surface.blit(self.scroll_bar.surface,(self.scroll_bar.x,self.scroll_bar.y))
        
class profile_screen(main_frame):
    def __init__(self,parent,user,other_profile=False):
        super().__init__(parent)
        self.user = user
        self.screen = None
        self.move_val = 0
        self.average_score_quicktype = 0
        self.average_score_recall = 0
        self.average_score_golf = 0
        self.other_profile = other_profile
        self.playtime_texts = []
        self.gamesplayed_texts = []
        if not self.other_profile:
            self.move_val = -33
        self.games = ['quicktype','integerrecall','golf']
        
        self.game_text = draw_text(user.upper(),30,True,WHITE)
        self.bg_title = surface_object(self.display_screen.w/1.2,50
                                       ,(self.display_screen.w-self.display_screen.w/1.2)/2,10,DDGREY)

        self.total_hours_bg = surface_object(self.display_screen.w/3,50
                                       ,self.display_screen.w/70,40,DDGREY)

        self.total_games_bg = surface_object(self.display_screen.w/3,50
                                       ,self.display_screen.w - self.display_screen.w/3,40,DDGREY)

        self.playtimeg_bg = surface_object(self.display_screen.w/4.1,35
                                       ,self.display_screen.w/70,40,DDGREY)

        self.gameplayed_bg = surface_object(self.display_screen.w/4.1,35
                                       ,self.display_screen.w/70,40,DDGREY)

        self.scoretitle_bg = surface_object(self.display_screen.w/3,35
                                       ,self.display_screen.w/70,40,DDGREY)

        self.game1_time_bg = surface_object(self.display_screen.w/4.1,35
                                       ,self.display_screen.w/70,40,DDGREY)
        self.game2_time_bg = surface_object(self.display_screen.w/4.1,35
                                       ,self.display_screen.w/70,40,DDGREY)
        self.game3_time_bg = surface_object(self.display_screen.w/4.1,35
                                       ,self.display_screen.w/70,40,DDGREY)


        self.game1_played_bg = surface_object(self.display_screen.w/4.1,35
                                       ,self.display_screen.w/70,40,DDGREY)
        self.game2_played_bg = surface_object(self.display_screen.w/4.1,35
                                       ,self.display_screen.w/70,40,DDGREY)
        self.game3_played_bg = surface_object(self.display_screen.w/4.1,35
                                       ,self.display_screen.w/70,40,DDGREY)

        self.game1_score_bg = surface_object(self.display_screen.w/3,35
                                       ,self.display_screen.w/70,40,DDGREY)
        self.game2_score_bg = surface_object(self.display_screen.w/3,35
                                       ,self.display_screen.w/70,40,DDGREY)
        self.game3_score_bg = surface_object(self.display_screen.w/3,35
                                       ,self.display_screen.w/70,40,DDGREY)
        
        self.back_button = button(self.display_screen,'<<<',startpos=(self.display_screen.w/70,self.display_screen.y+30),size=(self.display_screen.w/15,50),font_size =30,text_color=WHITE,bold=True)
        self.add_friend_button = button(self.display_screen,'+ ADD',startpos=(self.display_screen.w/12,self.display_screen.y+83),size=(self.display_screen.w/10,50),font_size =22,text_color=WHITE,bold=True)
        self.message_button = button(self.display_screen,'MESSAGE',startpos=(self.display_screen.w/5.4,self.display_screen.y+83),size=(self.display_screen.w/10,50),font_size =22,text_color=DDWHITE,bold=True)
        self.refresh_button = button(self.display_screen,'REFRESH',startpos = ((self.display_screen.w-200)/2
                                                                               ,self.display_screen.h+27)
                                     ,size=(200,50))
        self.refresh_profile()
        self.total_playtext = draw_text('TOTAL PLAYTIME: ' +str(self.total_playtime) + ' hours',25,True,WHITE)
        self.total_gametext = draw_text('TOTAL GAMES PLAYED: ' +str(self.total_games),25,True,WHITE)

        self.playtime_avg = draw_text('GAME PLAYTIME RANKING',20,True,WHITE)
        self.globalscore_avg = draw_text('SCORE VS GLOBAL AVERAGE',20,True,WHITE)
        self.gamesplayed_avg = draw_text('GAMES PLAYED RANKING',20,True,WHITE)

        self.game1 = draw_text('INTEGER RECALL',18,True,WHITE)
        self.game2 = draw_text('QUICKTYPE',18,True,WHITE)
        self.game3 = draw_text('GOLF GAME',18,True,WHITE)
        #self.playtime_texts.append(draw_text("{0:.<20} {1:.>20}".format(str((i+1))+'. '+x[0].upper()+':', str(x[1])+ ' h'),20,False,WHITE))
        for i,x in enumerate(self.ranking_playtime):
            self.playtime_texts.append(draw_text(str((i+1))+'. '+x[0].upper() + ' -- ' + str(x[1]) +' hours',20,False,WHITE))
        for i,x in enumerate(self.ranking_gamesplayed):
            self.gamesplayed_texts.append(draw_text(str((i+1))+'. '+x[0].upper() + ' -- ' + str(x[1]) +' games',20,False,WHITE))
    def draw(self,surface):
        self.display_screen.surface.blit(self.bg_title.surface
                                         ,((self.display_screen.w-self.display_screen.w/1.2)/2,30))
        self.display_screen.surface.blit(self.total_hours_bg.surface
                                         ,((self.display_screen.w-self.display_screen.w/1.2)/2,136+self.move_val))
        self.display_screen.surface.blit(self.total_games_bg.surface
                                         ,(self.display_screen.w - self.display_screen.w/2.4,136+self.move_val))
        
        self.display_screen.surface.blit(self.game_text.surface,(self.display_screen.w/10,34))

        self.display_screen.surface.blit(self.total_playtext.surface,(self.display_screen.w/9,143+self.move_val))
        self.display_screen.surface.blit(self.total_gametext.surface,(self.display_screen.w - self.display_screen.w/2.7,143+self.move_val))

        self.display_screen.surface.blit(self.playtimeg_bg.surface
                                         ,((self.display_screen.w-self.display_screen.w/1.2)/2,210+self.move_val))
        

        self.display_screen.surface.blit(self.game1_time_bg.surface
                                         ,((self.display_screen.w-self.display_screen.w/1.2)/2,255+self.move_val))
        self.display_screen.surface.blit(self.game2_time_bg.surface
                                         ,((self.display_screen.w-self.display_screen.w/1.2)/2,305+self.move_val))
        self.display_screen.surface.blit(self.game3_time_bg.surface
                                         ,((self.display_screen.w-self.display_screen.w/1.2)/2,355+self.move_val))

        self.display_screen.surface.blit(self.game1_played_bg.surface
                                         ,(self.display_screen.w - self.display_screen.w/3.05,255+self.move_val))
        self.display_screen.surface.blit(self.game2_played_bg.surface
                                         ,(self.display_screen.w - self.display_screen.w/3.05,305+self.move_val))
        self.display_screen.surface.blit(self.game3_played_bg.surface
                                         ,(self.display_screen.w - self.display_screen.w/3.05,355+self.move_val))

        self.display_screen.surface.blit(self.game1_score_bg.surface
                                         ,(self.display_screen.w - self.display_screen.w/1.5,255+self.move_val))
        self.display_screen.surface.blit(self.game2_score_bg.surface
                                         ,(self.display_screen.w - self.display_screen.w/1.5,305+self.move_val))
        self.display_screen.surface.blit(self.game3_score_bg.surface
                                         ,(self.display_screen.w - self.display_screen.w/1.5,355+self.move_val))    
        
        self.display_screen.surface.blit(self.game1_score_bg_compare.surface
                                         ,(self.display_screen.w - self.display_screen.w/1.5,255+self.move_val))
        self.display_screen.surface.blit(self.game2_score_bg_compare.surface
                                         ,(self.display_screen.w - self.display_screen.w/1.5,305+self.move_val))
       # self.display_screen.surface.blit(self.game3_score_bg_compare.surface
        #                                 ,(self.display_screen.w - self.display_screen.w/1.5,355+self.move_val))       

        self.display_screen.surface.blit(self.scoretitle_bg.surface
                                         ,(self.display_screen.w - self.display_screen.w/1.5,210+self.move_val))

        self.display_screen.surface.blit(self.gameplayed_bg.surface
                                         ,(self.display_screen.w - self.display_screen.w/3.05,210+self.move_val))
        self.display_screen.surface.blit(self.playtime_avg.surface,(self.display_screen.w/9,215+self.move_val))
        self.display_screen.surface.blit(self.globalscore_avg.surface,(self.display_screen.w/2.5,215+self.move_val))
        self.display_screen.surface.blit(self.gamesplayed_avg.surface,(self.display_screen.w/1.42,215+self.move_val))

        self.display_screen.surface.blit(self.game1.surface,(self.display_screen.w/2.28,262+self.move_val))
        self.display_screen.surface.blit(self.game2.surface,(self.display_screen.w/2.2,312+self.move_val))
        self.display_screen.surface.blit(self.game3.surface,(self.display_screen.w/2.2,362+self.move_val))
        for i,x in enumerate(self.playtime_texts):
            self.display_screen.surface.blit(x.surface,(self.display_screen.w/11,260+self.move_val+(i*50)))

        for i,x in enumerate(self.gamesplayed_texts):
            self.display_screen.surface.blit(x.surface,(self.display_screen.w - self.display_screen.w/3.15,260+self.move_val+(i*50)))
        
        

        surface.blit(self.display_screen.surface,(self.display_screen.x,self.display_screen.y))
        self.refresh_button.draw(surface)
        if self.other_profile:
            self.add_friend_button.draw(surface)
            self.back_button.draw(surface)
            if self.user in self.friends:
                self.message_button.draw(surface)

        
    def refresh_profile(self):
        temp = 0
        self.friends = get_table_data('friends')
        self.requests = get_table_data('requests')
        self.total_playtime = self.get_total_hours()
        self.total_games = self.get_total_games()
        self.ranking_playtime = self.get_playtime_ranking()
        self.ranking_gamesplayed = self.get_gamesplayed_ranking()
        self.average_score_recall = 0
        self.average_score_quicktype = 0
        self.average_score_golf = 0
        for x in get_players(''):
            self.average_score_recall += get_game_data('integerrecall','highscores',x)
            self.average_score_quicktype += get_game_data('quicktype','highscores',x)
            self.average_score_golf += get_game_data('golf','highscores',x)
        temp = len(get_players(''))
        score1=  get_game_data('integerrecall','highscores',self.user)
        if score1 == 0:
            score1 = 1
        score2 = get_game_data('quicktype','highscores',self.user)
        score3 = get_game_data('golf','highscores',self.user)
        self.average_score_recall = self.average_score_recall / temp
        self.average_score_quicktype = self.average_score_quicktype / temp
        if self.average_score_quicktype ==0:
            self.average_score_quicktype = 1
        self.average_score_golf = self.average_score_golf / temp
        if self.average_score_golf ==0:
            self.average_score_golf = 1
        if self.other_profile:
            if self.user in self.friends:
                self.add_friend_button.text = 'UNFRIEND'
                self.add_friend_button.text_color = DDWHITE
        temp2 = 0
        if self.average_score_recall / score1 > 1:
            temp2 = 0
        else:
            temp2 = self.average_score_recall / score1
        self.game1_score_bg_compare = surface_object((temp2) * self.display_screen.w/3+ 1,35
                                       ,self.display_screen.w/70,40,BLUE)
        if score2 / self.average_score_quicktype > 1:
            temp2 = 0
        else:
            temp2 = score2 / self.average_score_quicktype
        self.game2_score_bg_compare = surface_object((temp2 ) * self.display_screen.w/3+ 1,35
                                       ,self.display_screen.w/70,40,BLUE)
        #self.game3_score_bg_compare = surface_object((self.average_score_golf)/(score3) / self.display_screen.w/3 + 1,35
        #                               ,self.display_screen.w/70,40,BLUE)
        self.display_screen.surface.blit(surface_object(self.display_screen.w,self.display_screen.h,0,0,DGREY).surface,(0,0))
    def get_total_hours(self):
        mins=0
        for x in self.games:
            mins += get_game_data(x,'playtime',self.user)
        return round(mins/60,2)

    def get_total_games(self):
        amt=0
        for x in self.games:
            amt += get_game_data(x,'games_played',self.user)
        return amt

    def get_playtime_ranking(self):
        ranking = []
        for x in self.games:
            ranking.append((x,float(round(get_game_data(x,'playtime',self.user)/60,2))))
        return sorted(ranking, key=lambda tup:tup[1],reverse=True)

    def get_gamesplayed_ranking(self):
        ranking = []
        for x in self.games:
            ranking.append((x,get_game_data(x,'games_played',self.user)))
        return sorted(ranking, key=lambda tup:tup[1],reverse=True)
    
    def check_buttons(self):
        if self.other_profile:
            if self.add_friend_button.on_mouse_click() and not self.user in self.friends and not self.user in self.requests:
                send_friend_request(self.user)
                self.add_friend_button.text = 'SENT'
                self.add_friend_button.text_color = DDWHITE
                self.refresh_profile()
            elif self.add_friend_button.on_mouse_click() and self.user in self.friends:
                remove_friend(self.user)
                self.refresh_profile()
        if self.refresh_button.on_mouse_click():
            self.refresh_profile()
                


            
class stats_screen(main_frame):
    def __init__(self,parent):
        super().__init__(parent)
        self.select_bar = surface_object(self.display_screen.w/1.5,self.display_screen.h/14,round((self.display_screen.w - self.display_screen.w/1.5 )/2),10,DGREY)
        self.leader_board_display = surface_object(self.display_screen.w/1.3,self.display_screen.h/1.3,round((self.display_screen.w - self.display_screen.w/1.3 )/2),(self.display_screen.h-self.display_screen.h/1.3)/2,DDGREY)
        self.scroll_bar_frame = surface_object(self.w/70,self.h/1.55,self.x*7.5,(self.h - self.h/1.55)/2,SGREY)
        self.refresh_button = button(self.display_screen,'REFRESH',startpos = ((self.display_screen.w-200)/2,self.display_screen.h+27),size=(200,50))
        quicktype_scores = Leaderboard(user,'quicktype','global',parent,self.leader_board_display.w,self.leader_board_display.h
                                                   ,self.leader_board_display.x,self.h/3.9,True)

        integer_scores = Leaderboard(user,'integerrecall','global',parent,self.leader_board_display.w,self.leader_board_display.h
                                                   ,self.leader_board_display.x,self.h/3.9,True)

        golf_scores = Leaderboard(user,'golf','global',parent,self.leader_board_display.w,self.leader_board_display.h
                                                   ,self.leader_board_display.x,self.h/3.9,True)
        self.select_scores = button_grouper(self.select_bar,['QUICKTYPE','INTEGER RECALL','GOLF GAME'],button,frames=[quicktype_scores,integer_scores,golf_scores],pos=(0,self.display_screen.y+self.select_bar.y),sizes=(0,self.select_bar.h),centerx = True,style=1)
    def draw(self,surface):
        self.display_screen.surface.blit(self.select_bar.surface,(self.select_bar.x,self.select_bar.y))
        #self.leader_board_display.surface.blit(self.scroll_bar_frame.surface,(self.leader_board_display.w/4*3.8,(self.leader_board_display.h-self.scroll_bar_frame.h)/2))
        self.display_screen.surface.blit(self.leader_board_display.surface,(self.leader_board_display.x,self.leader_board_display.y))
        surface.blit(self.display_screen.surface,(0,self.display_screen.y))
        self.select_scores.draw(surface)
        self.refresh_button.draw(surface)
        
class button():
    def __init__(self,parent,text = None,startpos=(0,0),size=(None,None),text_color=DDWHITE, color = None
                 , style= 0 ,parent_frame = None,font_size=20,bold = False,center='CENTER',friends=False,outline = False,user='',image = None):
        self.text = text
        self.user=user
        self.friends = friends
        self.outline = outline
        self.parent = parent
        self.exclude = []
        self.startpos = startpos
        if color is None:
            self.color = DDGREY
        else:
            self.color =  color
        self.bold = bold
        self.center = center
        self.font_size = font_size
        self.style = style
        self.parent_frame = parent_frame
        if self.parent_frame is not None: self.parent_frame = parent_frame
        self.w = size[0]
        self.h = size[1]
        self.x = startpos[0]
        self.y = startpos[1]
        self.text_color = text_color
        self.style = style
        self.surface = surface_object(self.w,self.h,self.x,self.y,self.color)
        self.selected = False
        self.image = image
        if self.image is not None:
            self.text = ''
            self.image = pygame.image.load('./materials/'+self.image)
            self.image = pygame.transform.scale(self.image,(self.w,self.h))
    def draw(self,target,custom=False):
        self.font = pygame.font.SysFont('tahoma',self.font_size,self.bold)
        if self.on_mouse_hover() and not self.friends:
            self.text_surface = self.font.render(self.text,True,DWHITE)
            self.surface.set_color(SGREY)
            if self.image is not None:
                 pygame.draw.rect(target,WHITE,pygame.Rect(self.surface.x,self.surface.y,self.surface.w,self.surface.h),1) 
        else:
            self.text_surface = self.font.render(self.text,True,self.text_color)
            self.surface.set_color(self.color)
        if self.selected:
            self.text_surface = self.font.render(self.text,True,WHITE)
            self.surface.set_color(DGREY)
        if self.center == 'CENTER':
            self.center = (self.surface.w-self.text_surface.get_width())/2
        elif self.center == 'RIGHT':
            self.center = self.surface.w-self.text_surface.get_width()
        elif self.center == 'LEFT':
            self.center = self.surface.w/20
        if self.image is not None:
            self.surface.surface.blit(self.image,(0,0))
        self.surface.surface.blit(self.text_surface,(self.center,(self.surface.h-self.text_surface.get_height())/2))
        if custom:
            target.blit(self.surface.surface,(self.x-self.parent.x,self.y-self.parent.y))
        else:
            target.blit(self.surface.surface,(self.x,self.y))
        if self.style ==1 and self.selected:
            pygame.draw.rect(target,WHITE,pygame.Rect(self.surface.x,self.surface.y,self.surface.w,self.surface.h),2)
        if self.outline:
            pygame.draw.rect(target,WHITE,pygame.Rect(self.x-self.parent.x,self.y-self.parent.y,self.surface.w,self.surface.h),1)    
    def on_mouse_hover(self):
        hov = pygame.Rect(self.surface.x,self.surface.y,self.surface.w,self.surface.h).collidepoint(pygame.mouse.get_pos())
        for x in self.exclude:
            if not x.collidepoint(pygame.mouse.get_pos()):
                return False
        return hov       
    def on_mouse_click(self):
        return self.on_mouse_hover()
    def get_rect(self):
        return pygame.Rect(self.x-self.parent.x,self.y-self.parent.y,self.surface.w,self.surface.h)
    
class button_grouper():
    def __init__(self,parent,texts,button_type,sizes=(0,0),pos=(0,0),centerx = False,centery = False,frames=[None,None,None,None],offset=(0,0),style=0,gap=10):
        self.parent = parent
        #self.friends = friends
        self.pos = pos
        self.texts = texts
        self.button_type = button_type
        self.centerx = centerx
        self.centery = centery
        self.amount = len(texts)
        self.button_list = []
        self.frames = frames
        #self.button_list_profile = []
        for num,text in enumerate(texts):
            x,y=self.pos
            w,h=sizes
            if centerx:
                x = round(((self.parent.w-gap*(self.amount-1))/self.amount+gap) * (num) +self.parent.x + self.pos[0])
                w = round(((self.parent.w-gap*(self.amount-1))/self.amount))
            elif centery:
                y = round(((self.parent.h-gap*(self.amount-1))/self.amount+gap) * (num) + self.parent.y + self.pos[1])
                h = round(((self.parent.h-gap*(self.amount-1))/self.amount))
            else:
                x,y=self.pos
            self.button_list.append(self.button_type(self.parent,text,size=(int(w),int(h)),startpos=(x,y),parent_frame=frames[num],style=style))
            #self.button_list_profile.append(self.button_type(self.parent,'PROFILE',size=(int(w)/5,int(h)/2),startpos=(x + int(w) - int(w)/5,(y + int(h) + int(h)/2)/2),parent_frame=None,style=0,font_size=10,color=DGREY))
    def draw(self,surface):
        for x in self.button_list:
            x.draw(surface)

    def check_event(self,p_frame):
        for z in self.button_list:
            if z.on_mouse_click():
                for c in self.button_list:
                    c.selected = False
                z.selected = True
                return z.parent_frame
        return p_frame

session = session_var
user = user_login
launch = launcher(screen)

while True:
    screen.fill((0,0,0))
    launch.draw(screen)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.MOUSEBUTTONDOWN:
            launch.check_buttons()
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP:
            launch.check_scroll(event.type)
        elif event.type == pygame.KEYDOWN:
            if isinstance(launch.frame_selected,community_screen):
                if event.key == pygame.K_BACKSPACE:
                    if len(launch.community_menu.search_text) > 0:
                        del launch.community_menu.search_text[-1]
                elif len(launch.community_menu.search_text) < 25:
                    launch.community_menu.search_text.append(chr(event.key))
            if len(launch.chat_windows) != 0:
                for x in launch.chat_windows:
                    if x.selected:
                        if event.key == pygame.K_BACKSPACE:
                            if len(x.search_text) > 0:
                                del x.search_text[-1]
                        elif len(x.search_text) < 20:
                            ke = chr(event.key)
                            if str(ke) in 'abcdefghijklmnopqrstuvwxyz. ':
                                x.search_text.append(ke)

    pygame.display.update()
