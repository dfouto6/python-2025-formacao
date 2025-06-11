import random
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("TKAGG") #para usar o Tkinter como backend
import numpy as np
from tkinter import *
from tkinter import simpledialog
from tkinter import messagebox
import tkinter.font as tkFont
from tkinter.filedialog import askopenfile #apenas importa a função
import json
import os
import datetime

class minesweeper_gui:
#---------------------------------------------------------------------
    def __init__(self):
        #constantes
        self.__root=Tk()
        self.__root.resizable(width=False,height=False)#janela não pode ser resized pelo utilizador
        self.__custom_font=tkFont.Font(weight="bold")
        self.__text_color=["blue","green","red","darkblue","maroon","cyan","purple","grey"]
        self.__mine_symbol="\u2739"
        self.__flag_symbol="\u2691"
        self.__zero_symbol=" "
        self.__closed_symbol="C"
        self.__input_window=None

        #variáveis
        self.__list_of_cells=list() #lista de frames para representar células
        self.__list_of_labels=list() #lista de labels para mostrar os números de minas adjacentes
        self.__mines_board=list()
        self.__rows=0
        self.__columns=0
        self.__total_mines=0
        self.__mines_left=0
        self.__mines_labels=list() #guarda labels que mostram as minas em falta no canto inferior esquerdo: 0=simbolo de mina ; 1=número de minas
        self.__moves_left=0
        self.__max_moves=0
        self.__game_running=True
        self.__current_game="" #guarda a dificuldade do jogo corrente
        self.__input_rows=StringVar(value="9")
        self.__input_cols=StringVar(value="9")
        self.__input_mines=StringVar(value="10")
        self.__ok_pressed=False

        #começa com beginner game
        self.beginner_game_window()

        #menus
        self.menu_bar()
        
        #começar o loop de eventos
        self.__root.mainloop()
#---------------------------------------------------------------------
    def menu_bar(self):
        menubar=Menu(self.__root)
        file=Menu(menubar,tearoff=0)
        menubar.add_cascade(label="File",menu=file)
        newGame=Menu(file,tearoff=0)
        file.add_cascade(label="New Game",menu=newGame)
        newGame.add_command(label="Beginner",command=self.beginner_game_window)
        newGame.add_command(label="Advanced",command=self.advanced_game_window)
        newGame.add_command(label="Expert",command=self.expert_game_window)
        newGame.add_separator()
        newGame.add_command(label="Custom",command=self.custom_game_prompt)
        file.add_separator()
        file.add_command(label="Save",command=self.save_game)
        file.add_command(label="Load",command=self.load_game)
        file.add_separator()
        file.add_command(label="Exit",command=self.__root.destroy)
        self.__root.config(menu=menubar)
#---------------------------------------------------------------------
    def beginner_game_window(self):
        self.__current_game="Beginner"
        self.__root.title("Minesweeper - Beginner")
        self.draw_board(9,9,10)
#---------------------------------------------------------------------
    def advanced_game_window(self):
        self.__current_game="Advanced"
        self.__root.title("Minesweeper - Advanced")
        self.draw_board(16,16,40)
#---------------------------------------------------------------------
    def expert_game_window(self):
        self.__current_game="Expert"
        self.__root.title("Minesweeper - Expert")
        self.draw_board(16,30,99)
#---------------------------------------------------------------------
    def custom_game_window(self,rows,cols,mines):
        self.__current_game="Custom"+str(rows)+"x"+str(cols)
        self.__root.title("Minesweeper - Custom")
        self.draw_board(rows,cols,mines)
#---------------------------------------------------------------------
    def custom_game_prompt(self):
        self.__ok_pressed=False

        #janela de input
        self.__input_window=Toplevel(self.__root)
        self.__input_window.resizable(width=False,height=False)
        self.__input_window.title("Custom Game")
        
        #labels + entries
        vcmd=(self.__input_window.register(self.check_for_int))#faz com que os Entry widgets apenas aceitem números
        body = Frame(self.__input_window)
        label_row = Label(body, text="Number of Rows", justify=LEFT)
        label_row.grid(row=0, padx=0, sticky=W)
        row_input=Entry(body, name="rows",validate="all",validatecommand=(vcmd,"%P"),textvariable=self.__input_rows)
        row_input.bind('<FocusOut>', self.check_empty_inputs)
        row_input.grid(row=1, padx=0, sticky=W+E)
        row_input.select_range(0, END)
        label_col = Label(body, text="Number of Columns", justify=LEFT)
        label_col.grid(row=2, padx=0, sticky=W)
        col_input=Entry(body, name="cols",validate="all",validatecommand=(vcmd,"%P"),textvariable=self.__input_cols)
        col_input.bind('<FocusOut>', self.check_empty_inputs)
        col_input.grid(row=3, padx=0, sticky=W+E)
        label_mines = Label(body, text="Number of Mines", justify=LEFT)
        label_mines.grid(row=4, padx=0, sticky=W)
        mines_input=Entry(body, name="mines",validate="all",validatecommand=(vcmd,"%P"),textvariable=self.__input_mines)
        mines_input.bind('<FocusOut>', self.check_empty_inputs)
        mines_input.grid(row=5, padx=0, sticky=W+E)
        body.pack(padx=5, pady=5)

        #botões
        box=Frame(self.__input_window)
        ok_button = Button(box, text="OK", width=10, command=self.ok_button_press, default=ACTIVE)
        ok_button.pack(side=LEFT, padx=5, pady=5)
        cancel_button = Button(box, text="Cancel", width=10, command=self.cancel_button_press)
        cancel_button.pack(side=LEFT, padx=5, pady=5)
        box.pack()

        #intercepta o evento de fecho da janela
        self.__input_window.protocol("WM_DELETE_WINDOW",self.cancel_button_press)
        #janela de input centrada com a root
        simpledialog._place_window(self.__input_window, self.__root)
        self.__input_window.wait_visibility()
        self.__input_window.grab_set()
        self.__input_window.wait_window() #não avança enquanto a window não for fechada/destruida

        if self.__ok_pressed:
            self.custom_game_window(int(self.__input_rows.get()),
                                    int(self.__input_cols.get()),
                                    int(self.__input_mines.get()))

        #-----------------------------------------------------------------------------------
        # usa simpledialog.askinteger para pedir os três valores, 1 de cada vez
        #rows = simpledialog.askinteger("Custom Game - Rows","Number of Rows",initialvalue=9,parent=self.__root,minvalue=5,maxvalue=99)
        #if rows != None:
        #    cols = simpledialog.askinteger("Custom Game - Columns","Number of Columns",initialvalue=9,parent=self.__root,minvalue=5,maxvalue=99)
        #    if cols != None:
        #        mines = simpledialog.askinteger("Custom Game - Mines","Number of Mines",initialvalue=10,parent=self.__root,minvalue=1,maxvalue=rows*cols-9)
        #        if mines != None:
        #            self.custom_game_window(rows,cols,mines)
#---------------------------------------------------------------------
    def check_empty_inputs(self,event=None):
        if self.__input_rows.get()=="":
            self.__input_rows.set("0")
        if self.__input_cols.get()=="":
            self.__input_cols.set("0")
        if self.__input_mines.get()=="":
            self.__input_mines.set("0")
#---------------------------------------------------------------------
    def check_for_int(self, P):
        return str.isdigit(P) or str(P)==""
#---------------------------------------------------------------------
    def cancel_button_press(self):
        self.__root.focus_set()
        self.__input_window.destroy()
#---------------------------------------------------------------------
    def ok_button_press(self):
        #adaptado de simpledialog.py - é necessário o withdraw e o update_idletasks?
        if not self.validate_inputs():# se os valores não forem válidos, mostra mensagem e não continua
            return
        self.__ok_pressed=True
        self.__input_window.withdraw()
        self.__input_window.update_idletasks()
        self.cancel_button_press()
#---------------------------------------------------------------------
    def validate_inputs(self): #adaptado de simpledialog.py
        self.check_empty_inputs()
        parameters=("Rows","Columns","Mines")
        results=(self.__input_rows.get(),self.__input_cols.get(),self.__input_mines.get())
        LLs=(5,5,1)
        #limite de 25x25 - maior que isto e começa dar problemas: a janela não cabe no ecran, crasha, e ou problemas de recursividade na função open_adjacent
        ULs=(25,25,int(results[0])*int(results[1])-9) #número máximo de minas é dado por rows*cols-9
        for i,result in enumerate(results):
            if int(result) < LLs[i]:
                messagebox.showwarning(
                    "Too small",
                    f"The allowed minimum value for the number of {parameters[i]} is {LLs[i]}."
                    "Please try again."
                )
                return 0
            if int(result) > ULs[i]:
                messagebox.showwarning(
                    "Too large",
                    f"The allowed maximum value for the number of {parameters[i]} is {ULs[i]}. "
                    "Please try again."
                )
                return 0
        return 1
#--------------------------------------------------------------------- 
    def save_game(self):
        if self.__game_running:
            date=datetime.datetime.now()
            file_name=date.strftime(f"%Y_%m_%d_%H_%M_%S_{self.__current_game}.json")
            file_path=os.path.join(os.path.dirname(__file__), f"saves\\{file_name}") #path para a pasta "saves" na mesma pasta do script
            
            labels_dict=dict()
            mines_list=list()
            #self.__mines_board e self.__list_of_labels têm o mesmo tamanho
            for row,all_row in enumerate(self.__mines_board):
                for col,_ in enumerate(all_row):
                    if self.is_mine(row,col):
                        mines_list.append((row,col))
                    if self.__list_of_labels[row][col]!=self.__closed_symbol: #há label em (row,col)
                        label_symbol=self.__list_of_labels[row][col].cget("text")
                        if labels_dict.get(label_symbol)==None:
                            labels_dict[label_symbol]=[(row,col)] #se ainda não houver key com o simbolo, cria a key com uma lista de coordenadas
                        else:
                            labels_dict[label_symbol].append((row,col)) #key já existe, adiciona as coordenadas à lista

            json_object=json.dumps({
                "Dificulty":self.__current_game,
                "TotalMines":self.__total_mines,
                "MinesLeft":self.__mines_left,
                "MovesLeft":self.__moves_left,
                "Labels":labels_dict,
                "MinesBoard":mines_list
                },indent=4)
            with open(file_path,"w") as file:
                file.write(json_object)
            messagebox.showinfo("Game Saved",f"Game saved:\n{file_path}")
        else:
            #print("Game is not running")
            pass
#---------------------------------------------------------------------
    def load_game(self):
        file=askopenfile(mode="r",
                    title="Load Minesweeper Save",
                    filetypes=[("Save File","*.json")],
                    initialdir=os.path.join(os.path.dirname(__file__), "saves")
                    )
        if file is None:
            pass
            #print("No file selected")
        else:
            try:
                data=json.load(file)
                
                total_mines=data["TotalMines"]
                if not type(total_mines)==int:
                    raise Exception("\"TotalMines\" is NOK")
                
                #TODO custom game
                if data["Dificulty"]=="Beginner":
                    self.beginner_game_window()
                elif data["Dificulty"]=="Advanced":
                    self.advanced_game_window()
                elif data["Dificulty"]=="Expert":
                    self.expert_game_window()
                elif data["Dificulty"].startswith("Custom"):
                    row,col=data["Dificulty"].split("Custom")[1].split("x")
                    self.custom_game_window(int(row),int(col),total_mines)
                else:
                    raise Exception("\"Dificulty\" is NOK")

                mines_left=data["MinesLeft"]
                if not type(mines_left)==int:
                    raise Exception("\"MinesLeft\" is NOK")
                self.__mines_left=mines_left
                self.update_mines_left("")
                
                moves_left=data["MovesLeft"]
                if not type(moves_left)==int:
                    raise Exception("\"MovesLeft\" is NOK")
                self.__moves_left=moves_left
                
                mines_list=data["MinesBoard"]
                if len(mines_list)==total_mines:
                    self.__mines_board=[[self.__closed_symbol for _ in range(self.__columns)] for _ in range(self.__rows)] #inicializa a board de minas
                    for (row,col) in mines_list:
                        if (row in range(0,self.__rows)) and (col in range(0,self.__columns)):
                            self.__mines_board[row][col]=self.__mine_symbol
                        else:
                            raise Exception("\"MinesBoard\" is NOK")
                else:
                    raise Exception("\"MinesBoard\" is NOK")

                labels=data["Labels"]
                for symbol,xy_list in labels.items():
                    if symbol in [self.__zero_symbol,self.__flag_symbol,"1","2","3","4","5","6","7","8"]:
                        for (row,col) in xy_list:
                            if row in range(self.__rows) and col in range(self.__columns):
                                if symbol==self.__flag_symbol:
                                    self.put_label_in_cell(row,col,"red",self.__flag_symbol,"SystemButtonFace","raised")
                                    self.__list_of_labels[row][col].bind("<Button>",lambda event,row=row,column=col: self.frame_click_handler(event,row,column))
                                else:
                                    if symbol==self.__zero_symbol:
                                        mines=0
                                    else:
                                        mines=int(symbol)
                                    text_color=self.__text_color[max(0,mines-1)]
                                    self.put_label_in_cell(row,col,text_color,symbol,"SystemButtonFace","sunken")
                            else:
                               raise Exception("\"Labels\" is NOK") 
                    else:
                        raise Exception("\"Labels\" is NOK")
                #print("Load OK")
            except Exception as error:
                print("Save file is not valid")
                print(error)
                self.beginner_game_window() #se não conseguiu fazer load correctamente, cria um jogo beginner
            file.close()
#---------------------------------------------------------------------
    def frame_click_handler(self,event,row,col):
        text_bg="SystemButtonFace"
        text=""

        if self.__game_running:
            if self.__list_of_labels[row][col]==self.__closed_symbol:# célula fechada e sem flag
                if event.num==1: #left click
                    mines=self.calculate_mine_number(row,col)
                    #se a primeira célula a abrir for mina ou tiver minas adjacentes, move as minas de sitio
                    if (self.__max_moves==self.__moves_left):
                        if self.is_mine(row,col) or mines>0:
                            self.reposition_mines(row,col)
                            mines=0

                    if self.is_mine(row,col):
                        text=self.__mine_symbol #também usado para sinalizar no fim da função que se clicou numa mina
                        text_color="black"
                        text_bg="red"
                    else:
                        self.__moves_left-=1
                        if mines==0: #abrir todas as células adjacentes que não forem minas
                            self.__list_of_labels[row][col]=self.__zero_symbol #para sinalizar que a célula está a ser processada
                            self.open_adjacent(row,col)
                            text=self.__zero_symbol
                        else:
                            text=str(mines)
                        text_color=self.__text_color[max(0,mines-1)]
                    self.put_label_in_cell(row,col,text_color,text,text_bg,"sunken")

                else: #right or middle click -> colocar flag
                    self.update_mines_left("-")
                    self.put_label_in_cell(row,col,"red",self.__flag_symbol,text_bg,"raised")
                    self.__list_of_labels[row][col].bind("<Button>",lambda event,row=row,column=col: self.frame_click_handler(event,row,column))
                
            elif self.__list_of_labels[row][col].cget("text")==self.__flag_symbol:# tem label de flag:
                self.update_mines_left("+") 
                self.__list_of_labels[row][col].destroy()
                self.__list_of_labels[row][col]=self.__closed_symbol

            if self.__moves_left==0 or text==self.__mine_symbol: #acabou o jogo
                if self.__moves_left==0:
                    game_status="WIN"
                else:
                    game_status="LOSE"
                self.show_mines()
                self.__game_running=False
                self.game_over(game_status)
#---------------------------------------------------------------------
    def draw_board(self,nRows,nColumns,nMines):
        self.__game_running=True
        self.__moves_left=nRows*nColumns-nMines
        self.__max_moves=nRows*nColumns-nMines
        self.__rows=nRows
        self.__columns=nColumns
        self.__total_mines=nMines
        self.__mines_board=[[self.__closed_symbol for _ in range(nColumns)] for _ in range(nRows)]
        self.place_mines(nMines)

        #destroi as frames que representam células
        for row in self.__list_of_cells:
            for cell in row:
                cell.destroy()
        self.__list_of_cells=list()

        #destroi as labels com os números de minas adjacentes
        for row in self.__list_of_labels:
            for label in row:
                if label != self.__closed_symbol:
                    label.destroy()
        self.__list_of_labels=[[self.__closed_symbol for _ in range(nColumns)] for _ in range(nRows)]

        #destroi as labels de minas em falta
        for label in self.__mines_labels:
            label.destroy()
        self.__mines_labels=list()

        #cria células usando frames
        for row in range(nRows):
            row_list=list()
            for i,column in enumerate(range(nColumns)):
                frame=Frame(self.__root,borderwidth=2,relief="raised",width=30,height=30)#quadrado 30x30. estes valores são usados no cálculo do tamanho da janela
                frame.grid_propagate(False)#evita o resize da frame ao acrescentar widgets
                if i == 0:
                    frame.grid(column=column,row=row,padx=[5,0]) #afastar do limite esquerdo da janela
                else:
                    frame.grid(column=column,row=row,padx=0)
                frame.bind("<Button>",lambda event,row=row,column=column: self.frame_click_handler(event,row,column))
                row_list.append(frame)
            self.__list_of_cells.append(row_list)

        #label para mostrar minas em falta
        self.__mines_labels.append(Label(self.__root,text=self.__mine_symbol,bg="red",font=self.__custom_font,relief=RAISED))
        self.__mines_labels[0].grid(column=0, row=nRows,pady=15,sticky=E)
        self.__mines_labels.append(Label(self.__root,text=f"{nMines:03d}",font=self.__custom_font,relief=RAISED))
        self.__mines_labels[1].grid(column=1, row=nRows,pady=15,columnspan=2,sticky=W)
        self.__mines_left=nMines

        #centrar a janela
        w=nColumns*30+10 #número de colunas, vezes width da célula, mais algum espaço à direita
        h=nRows*30+56 #número de linhas, vezes height da célula, mais algum espaço para a label com o número de minas
        ws=self.__root.winfo_screenwidth()#width do ecran em pixeis
        hs=self.__root.winfo_screenheight()#height do ecran em pixeis
        x=(ws/2) - (w/2) #coordenadas para centrar
        y=(hs/2) - (h/2)
        self.__root.geometry("%dx%d+%d+%d" % (w,h,x,y))
#---------------------------------------------------------------------
    def place_mines(self,nMines):
        placed_mines=0
        while(placed_mines<nMines):
            row=random.randrange(0,self.__rows)
            col=random.randrange(0,self.__columns)
            if not self.is_mine(row,col):
                self.__mines_board[row][col]=self.__mine_symbol
                placed_mines+=1
#---------------------------------------------------------------------
    def is_mine(self,row,col):
        if self.__mines_board[row][col]==self.__mine_symbol:
            return True
        return False
#---------------------------------------------------------------------   
    def is_open(self,row,col):
        if self.__list_of_labels[row][col]==self.__closed_symbol:# não tem label e ainda está fechado
            return False
        if self.__list_of_labels[row][col]==self.__zero_symbol:# não tem label mas está a ser processado 
            return True
        # em príncipio, se chegou aqui é porque já existe label nesta posição
        # o programa vai crashar se assim não for
        if self.__list_of_labels[row][col].cget("text")==self.__flag_symbol:# tem label de flag
            return False
        return True # tem label com número
#---------------------------------------------------------------------
    def calculate_mine_number(self,row,col):
        # calculo do número de minas adjacentes à célula (row,col)
        # offsets:
        #  (-1,-1) | ( 0, -1 ) | (+1,-1)
        # ------------------------------
        #  (-1, 0) | (row,col) | (+1, 0)
        # ------------------------------
        #  (-1;+1) | ( 0, +1 ) | (+1,+1)
        offsets=((-1,-1),(0,-1),(+1,-1),(-1,0),(+1,0),(-1,+1),(0,+1),(+1,+1))
        mine_number=0
        for off_row,off_col in offsets:
            curr_row=row+off_row
            curr_col=col+off_col
            if (curr_row in range(0,self.__rows)) and (curr_col in range(0,self.__columns)): #verifica se a célula adjacente está dentro do tabuleiro do jogo
                if self.is_mine(curr_row,curr_col):
                    mine_number+=1
        return mine_number
#---------------------------------------------------------------------
    def reposition_mines(self,row,col):
        offsets=((0,0),(-1,-1),(0,-1),(+1,-1),(-1,0),(+1,0),(-1,+1),(0,+1),(+1,+1))
        mines2move=0
        for off_row,off_col in offsets:
            curr_row=row+off_row
            curr_col=col+off_col
            if (curr_row in range(0,self.__rows)) and (curr_col in range(0,self.__columns)): #verifica se a célula adjacente está dentro do tabuleiro do jogo
                if self.is_mine(curr_row,curr_col):
                    mines2move+=1
                self.__mines_board[curr_row][curr_col]=self.__mine_symbol #coloca mina provisória para que a função place_mines não coloque nesta celula
        
        self.place_mines(mines2move)

        #remove as minas provisórias
        for off_row,off_col in offsets:
            curr_row=row+off_row
            curr_col=col+off_col
            if (curr_row in range(0,self.__rows)) and (curr_col in range(0,self.__columns)):
                self.__mines_board[curr_row][curr_col]=self.__closed_symbol
#---------------------------------------------------------------------
    def open_adjacent(self,row,col):
        offsets=((-1,-1),(0,-1),(+1,-1),(-1,0),(+1,0),(-1,+1),(0,+1),(+1,+1))
        for off_row,off_col in offsets:
            curr_row=row+off_row
            curr_col=col+off_col
            if (curr_row in range(0,self.__rows)) and (curr_col in range(0,self.__columns)): #verifica se a célula adjacente está dentro do tabuleiro do jogo
                if self.is_mine(curr_row,curr_col) or self.is_open(curr_row,curr_col):
                    continue
                else:
                    self.__moves_left-=1
                    mines=self.calculate_mine_number(curr_row,curr_col)
                    if mines==0:#abrir todas as células adjacentes que não forem minas
                        self.__list_of_labels[curr_row][curr_col]=self.__zero_symbol #para sinalizar que a célula está a ser processada
                        self.open_adjacent(curr_row,curr_col)
                        text=self.__zero_symbol
                    else:
                        text=str(mines)
                    
                    text_color=self.__text_color[max(0,mines-1)]
                    self.put_label_in_cell(curr_row,curr_col,text_color,text,"SystemButtonFace","sunken")
#---------------------------------------------------------------------   
    def update_mines_left(self,operation):
        if operation=="+":
            self.__mines_left+=1
        elif operation=="-":
            self.__mines_left-=1
        self.__mines_labels[1].config(text=f"{max(self.__mines_left,0):03d}")
#--------------------------------------------------------------------- 
    def show_mines(self):
        for row in range(self.__rows):
            for col in range(self.__columns):
                if self.is_mine(row,col) and not self.is_open(row,col):
                    self.put_label_in_cell(row,col,"black",self.__mine_symbol,"SystemButtonFace","sunken")
#---------------------------------------------------------------------
    def put_label_in_cell(self,row,col,text_color,text,text_bg,relief):
        label=Label(self.__list_of_cells[row][col],font=self.__custom_font,fg=text_color,text=text,bg=text_bg)
        label.grid(row=0,column=0,sticky="") #para centrar a label na frame 1/3
        self.__list_of_cells[row][col].configure(relief=relief,bg=text_bg)
        self.__list_of_cells[row][col].grid_rowconfigure(0,weight=1) #para centrar a label na frame 2/3
        self.__list_of_cells[row][col].grid_columnconfigure(0,weight=1) #para centrar a label na frame 3/3
        self.__list_of_labels[row][col]=label
#---------------------------------------------------------------------
    def game_over(self,game_status):
        plt.rcParams['toolbar'] = 'None' #esconde a toolbar que aparece no rodapé da janela
        line_color="yellow"
        if game_status=="WIN":
            background_color="green"
            title_text="***** YOU WIN *****"
            figure_title="WIN"
        else:
            background_color="red"
            title_text="***** !BOOM! *****\n**** YOU LOSE ****"
            figure_title="LOSE"
        
        px = 1/plt.rcParams['figure.dpi']  # pixel in inches
        w=480
        h=480
        fig,ax=plt.subplots(figsize=(w*px, h*px),facecolor=background_color,label=figure_title)
        self.center_figure(fig,w,h)
        plt.title(title_text,fontsize="xx-large",color=line_color)
        plt.axis("off")

        #boca
        x=np.linspace(-2,2,25)
        if game_status=="WIN": # :)
            y=0.25*x*x-2
            y2=0.1*x*x-1.4
            title="VICTORY"
        else: # :(
            y=-0.25*x*x-0.5
            y2=-0.1*x*x-1.1
            title="DEFEAT"
        ax.plot(x,y,color=line_color)
        ax.plot(x,y2,color=line_color)
        
        #circulo da cara
        angle=np.arange(0,2*np.pi,0.01)
        radius=3
        x=radius*np.cos(angle)
        y=radius*np.sin(angle)
        ax.plot(x,y,color=line_color)

        #olho esquerdo
        radius=0.3
        x=radius*np.cos(angle)-1
        y=radius*np.sin(angle)+1.5
        ax.plot(x,y,color=line_color)

        #olho direito
        x=radius*np.cos(angle)+1
        ax.plot(x,y,color=line_color)
        
        plt.show()
#---------------------------------------------------------------------   
    def center_figure(self,fig,width,height):
        ws=self.__root.winfo_screenwidth() #width do ecran em pixeis
        hs=self.__root.winfo_screenheight() #height do ecran em pixeis
        x=(ws/2) - (width/2) #coordenadas para centrar
        y=(hs/2) - (height/2)
         
        #aquando da importação do matplotlib o backend é forçado a "TKAGG"
        fig.canvas.manager.window.wm_geometry("+%d+%d" % (x, y)) #Move figure's upper left corner to pixel (x, y)
        fig.canvas.manager.window.resizable(False,False) #disable do resize da window
#---------------------------------------------------------------------

#limpa o output da consola
os.system("cls" if os.name=="nt" else "clear")
game=minesweeper_gui()