'''
TODO
    hacer grafico dv vs dt ajustar y sacar alpha
        graficar por separado calentar y enfriar
    plotear delta temps contra los volts para las resistencias
    comparar graficos del mismo proceso(enfriando con y sin voltage, etc)
    estimar efecto joule

'''
from marco import experimento
import warnings
import numpy as np
import matplotlib.pyplot as plt
from uncertainties import unumpy as un

termo = experimento("termometria/diados/tempsposta")
# termo.mediciones(claves=["temp",'csv'])
archivos = [
        ['tempnuevas_apagar_1amp_2.csv',18.0,0,0
        ],['tempnuevas_enfriar_1amp_2.csv',18.0,0.97,0.7
        ],['tempnuevas_apagado_1-5amp_1.csv',18.0,0,0
        ],['tempnuevas_enfriar_1amp_3.csv',18.0,1,0.7
        ],['tempnuevas_enfriar_1amp_4.csv',18.0,1,0.7
        ],['tempnuevas_enfriar_1-5amp_1.csv',18.0,1.5,1.1

        ],['tempnuevas_enfriar_2amp_1.csv',18.0,1.98,1.4

        # ],['tempnuevas_calentar_1-75amp_1.csv',18.0,1.74,1.3
        # ],['tempnuevas_enfriar_1-75amp_prueba.csv',18.0

        # ],['temperaturas_recalentar_1-75_1.csv',18.0,1.74,1.7
        ],['temperaturas_enfriar_1-75amp_2.csv',18.0,1.74,1.2
        # ],['temperaturas_recalentar_2amp_1.csv',18.0,2.01,1.5
        ],['temperaturas_enfriar_1-25amp_1.csv',18.0,1.25,0.9

        ],['temperaturas_res_1amp_1.csv',18.5,0,0
        ],['temperaturas_res_enfriando_03amp_1.csv',18.5,0,0
        ],['temperaturas_res_05amp_1.csv',18.5,0.49,4.7
        ],['temperaturas_res_enfriando_05amp_1.csv',19.0,0,0

        ]]


# print(len(termo.mediciones))
# print(len(archivos))
def plotear(labels,*args):
    for i,var in enumerate(args):
        try:
            varerr = un.std_devs(var)
            varvals = un.nominal_values(var)

            varmenos = varvals - varerr
            varmas = varvals + varerr

            # plt.errorbar(S,varvals,xerr=Serr,yerr=valerr,fmt='.',label=labels[i])
            plt.plot(S.ravel(),varvals,'.',label=labels[i])
            plt.fill_between(S.ravel(),varmenos.ravel(),varmas.ravel(), alpha=0.5)
        except TypeError:
            print('no andan lo errores')
            plt.plot(S,var,'.',label=labels[i])

    plt.title(medicion.split('.')[0].replace('_',' '))
    plt.legend(loc='best')
    plt.ylabel('Temperatura (C)')
    plt.xlabel('Tiempo (S)')
    plt.show()
    # plt.savefig(medicion.split('.')[0])

def errorT(A,err,tamb):
    e = err * np.ones(np.shape(A))
    Ar = un.uarray(A,e)
    Ar = Ar + un.uarray(tamb,0.5)
    return Ar

def errorV(A,err):
    e = err * np.ones(np.shape(A))
    Ar = un.uarray(A,e)
    return Ar

def rendimiento(A1,A2):
    #veo de las temperaturas cual minimo es el menor y saco el dT
    #correspondiente
    minimo = min(np.min(A1),np.min(A2))
    base = T1[T1==minimo]
    if base.size > 0:
        resultado = T2[T1==minimo] - base
        # print(medicion,resultado)
    else:
        warnings.warn('estan dados vuelta')
        base = T2[T2==minimo]
        resultado = T1[T2==minimo] - base
        # print(medicion,resultado)
    return resultado

def rendimiento2(A1,A2):
    #uso los ultimos valores de cada medicion pq son mas estables.
    #vale para todas las mediciones salvo las que tienen prendido y apagado
    resultado = A1[-1] - A2[-1]
    if resultado < 0:
        resultado = A2[-1] - A1[-1]
    return resultado


deltas = []
amps = []
volts = []
for medicion,tamb,amp,volt in archivos:
    try:
        labels = ['Termo1','Termo2']
        T1,T2,S = termo.cargar(medicion,3)
        T1 = errorT(T1,2.2,tamb)
        T2 = errorT(T2,2.2,tamb)
        # print(medicion)
        delta = rendimiento2(T1,T2)
        if medicion == 'tempnuevas_enfriar_1amp_3.csv':
            delta = rendimiento(T1,T2)
        deltas.append(delta)
        amps.append(amp)
        volts.append(volt)
	# plotear(labels,T1,T2)
	# plotear('Delta T',T1-T2)
    except ValueError:
        continue
        labels = ['Termo1','Termo2','Voltaje']
        T1,T2,V,S = termo.cargar(medicion,4)
        T1 = errorT(T1,2.2,tamb)
        T2 = errorT(T2,2.2,tamb)
        V = errorV(V,1)
        # plotear(labels,T1,T2)
        # plotear(['Delta T', 'Voltaje',T1-T2,V)
# deltas = np.asarray(deltas)
# labels = ['delta T','Amperaje']

# deltaTmax = max(deltas)
# deltaTnorm = deltas / deltaTmax

deltas = np.asarray(deltas)
volts = np.asarray(volts)
# for i in range(len(deltas)):
    # plt.plot(un.nominal_values(deltas),volts,'.')
    # xy=(un.nominal_values(deltas)[i],volts[i])
    # plt.annotate(archivos[i][0],xy=xy)
    # xy_=(volts[i],un.nominal_values(deltas)[i])
    # plt.annotate(archivos[i][0],xy=xy,xytext=xy_,textcoords='offset points')

dT = un.nominal_values(deltas).ravel()
dTerr = un.std_devs(deltas).ravel()

plt.errorbar(dT,volts,xerr=dTerr,yerr=0.1, fmt='ok')

z,cov = np.polyfit(dT,volts,1,cov=True)
zerr = np.sqrt(cov[0,0] * np.sqrt(9))

polinomio = np.poly1d(z)

plt.rcParams['mathtext.default']= 'regular'

x = np.linspace(min(dT),max(dT),100)
plt.plot(x,polinomio(x),'--k',label=r'$\alpha =(62.9 \pm 4.5) \ mV \ K^{-1}$')
# plt.plot(x,polinomio(x),'--k',label=fr'$\alpha =({1e3*z[0]:.1f} \pm {1e3*zerr:.1f}) \  mV\ K^{-1}$')

print(volts)
plt.ylabel(r'$Voltaje\ (V)$')
plt.xlabel(r'$\Delta T\ estacionario\ (K)$')
plt.legend(loc='upper left', framealpha=1)
plt.grid(True)
# plt.show()
plt.savefig('alfaenfriar.png', dpi=300)
