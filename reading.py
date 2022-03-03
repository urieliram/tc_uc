import json

def reading(file):
    with open(file) as json_file:
        md = json.load(json_file)
        
    G       = []   ## generators number
    T       = []   ## periodos de tiempo
    S       = {}   ## eslabones de costo variable de arranque
    L       = {}   ## eslabones de costo en piecewise
    C       = {}   ## cost of segment of piecewise
    Pb      = {}   ## power of segment of piecewise
    De      = {}   ## load
    R       = {}   ## reserve_requirement
    Pmin    = {}   ## power min
    Pmax    = {}   ## power max
    RU      = {}   ## ramp_up_limit", "ramp_up_60min"
    RD      = {}   ## ramp_down_limit", "ramp_down_60min"
    SU      = {}   ## ramp_startup_limit", "startup_capacity"
    SD      = {}   ## ramp_shutdown_limit", "shutdown_capacity"
    TU      = {}   ## time_upminimum
    TD      = {}   ## time_down_minimum
    D       = {}   ## number of hours generator g is required to be off at t=1 (h).
    U       = {}   ## number of hours generator g is required to be on at t=1 (h).
    pc_0    = {}   ## power_output_t0
    mpc     = {}   ## cost of generator g running and operating at minimum production Pmin ($/h).
    C       = {}   ## 
    Cs      = {}   ## Costo de cada escalón del conjunto S de la función de costo variable de arranque.
    Tmin    = {}   ## lag de cada escalón del conjunto S de la función de costo variable de arranque.
    Startup = {}   ## start-up  cost
        
    time_periods = md['time_periods']
    demand       = md['demand']  
    reserves     = md['reserves']  

    for t in range(1, time_periods+1):
        T.append(t)    
    De   = dict(zip(T, demand))
    R    = dict(zip(T, reserves))
    
    names_list = []
    i = 1
    ## Se obtiene nombre de los generadores y número
    for gen in md['thermal_generators']:  
        names_list.append(gen)
        G.append(i)
        i+=1
        
    must_run             = []
    power_output_minimum = []
    power_output_maximum = []
    ramp_up_limit        = []
    ramp_down_limit      = []
    ramp_startup_limit   = []
    ramp_shutdown_limit  = []
    time_up_minimum      = []
    time_down_minimum    = []
    power_output_t0      = []
    unit_on_t0           = []
    time_up_t0           = []
    time_down_t0         = []   
    startup              = []
    piecewise_production = []
    Piecewise            = []
    Startup              = []
    Ulist                = []
    Dlist                = []
    pc_0_list            = []
    u_0_list             = []
    
    ## To get the data from the generators
    i=1 ## Cuenta los generadores
    for gen in names_list:  
        must_run.append(md['thermal_generators'][gen]["must_run"]) #0,
        power_output_minimum.append(md['thermal_generators'][gen]["power_output_minimum"])#80
        power_output_maximum.append(md['thermal_generators'][gen]["power_output_maximum"])#300.0
        ramp_up_limit.append(md['thermal_generators'][gen]["ramp_up_limit"])#50
        ramp_down_limit.append(md['thermal_generators'][gen]["ramp_down_limit"])#30
        ramp_startup_limit.append(md['thermal_generators'][gen]["ramp_startup_limit"])#100
        ramp_shutdown_limit.append(md['thermal_generators'][gen]["ramp_shutdown_limit"])#80
        time_up_minimum.append(md['thermal_generators'][gen]["time_up_minimum"])#3
        time_down_minimum.append(md['thermal_generators'][gen]["time_down_minimum"])#2
        power_output_t0.append(md['thermal_generators'][gen]["power_output_t0"])#120
        unit_on_t0.append(md['thermal_generators'][gen]["unit_on_t0"])#1
        time_up_t0.append(md['thermal_generators'][gen]["time_up_t0"])#1
        time_down_t0.append(md['thermal_generators'][gen]["time_down_t0"])#0        
        startup = (md['thermal_generators'][gen]["startup"]) # variable start-up cost
        piecewise_production = md['thermal_generators'][gen]["piecewise_production"] #piecewise cost
        
        ## Para obtener los piece del costo de los generadores
        lista_aux = []
        lista = []
        j = 1
        for piece in piecewise_production:
            lista_aux.append((piece['mw'],piece['cost']))
            lista.append(j)
            j+=1            
        Piecewise.append(lista_aux)
        L[i] = lista
        
        ## Para obtener segmentos del costo variables de arranque
        lista_aux2 = []
        lista2 = []
        j = 1
        for segment in startup:
            lista_aux2.append((segment['lag'],segment['cost']))
            lista2.append(j)
            j+=1            
        Startup.append(lista_aux2)
        S[i] = lista2
                
        ## Validaciones
        if power_output_t0[i-1] !=0 and unit_on_t0[i-1] == 0:
            print('Error: The generator ',str(i),' cannot be off and its output greater than zero')
            quit()
        if time_down_t0[i-1] !=0 and unit_on_t0[i-1] != 0:
            print('Error: The generator  ',str(i),' cannot be off and on at the same time')
            quit()
                    
        ## Caso prendido
        if unit_on_t0[i-1] > 0:
            u_0_list.append(1)
            aux = time_up_minimum[i-1] - time_up_t0[i-1]
            if aux<=0:
                aux=0
            Ulist.append(aux)
            Dlist.append(0)            
        ## Caso apagado
        if unit_on_t0[i-1] <= 0: 
            u_0_list.append(0)   
            aux = time_down_minimum[i-1] - time_down_t0[i-1]
            if aux <= 0:
                aux = 0
            Ulist.append(0)
            Dlist.append(aux)
            
        aux = power_output_t0[i-1] - power_output_minimum[i-1]
        if aux<0:
            aux=0
        pc_0_list.append(aux)
            
        i+=1 ## Se incrementa un generador    
                
    ## Se extraen los diccionarios Pb y C de la lista de listas Piecewise    
    k=0; n=0
    for i in Piecewise:
        s=len(i)
        k=k+1
        n=0
        for j in i:
            n=n+1
            # print(k,",",n,",",s,",",j[0],",",j[1])
            Pb[k,n] = j[0]
            C[k,n]  = j[1]
            ## Se calcula el costo mínimo de operación mpc
            if n==1:
                mpc[k] = j[0]*j[1]
                
    ## Se extraen los diccionarios Tmin y Cs de la lista de listas Startup    
    k=0; n=0
    for i in Startup:
        s=len(i)
        k=k+1
        n=0
        for j in i:
            n=n+1
            # print(k,",",n,",",s,",",j[0],",",j[1])
            Tmin[k,n] = j[0]
            Cs[k,n]   = j[1] 
    
    ## Aqui se pasan de arreglos a diccionarios como los usa Pyomo
    Pmax = dict(zip(G, power_output_maximum))
    Pmin = dict(zip(G, power_output_minimum))
    TU   = dict(zip(G, time_up_minimum))     
    TD   = dict(zip(G, time_down_minimum))  
    u_0  = dict(zip(G, u_0_list))          
    U    = dict(zip(G, Ulist))              
    D    = dict(zip(G, Dlist))                
    SU   = dict(zip(G, ramp_startup_limit))
    SD   = dict(zip(G, ramp_shutdown_limit))
    RU   = dict(zip(G, ramp_up_limit))
    RD   = dict(zip(G, ramp_down_limit))
    pc_0 = dict(zip(G, pc_0_list))  
    names = dict(zip(G, names_list))  
       
    return G,T,L,S,Pmax,Pmin,TU,TD,De,R,u_0,U,D,SU,SD,RU,RD,pc_0,Pb,C,mpc,Cs,Tmin,names
          #G,T,L,S,Pmax,Pmin,TU,TD,De,R,u_0,U,D,SU,SD,RU,RD,mpc,Pb,C,Cs,Tmin,fixShedu,relax,ambiente