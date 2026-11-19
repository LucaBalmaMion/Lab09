import copy

from database.parco_DAO import ParcoDAO
from database.escursione_DAO import EscursioneDAO
from database.punto_interesse_DAO import PuntoInteresseDAO
from model.escursione import Escursione


class Model:
    def __init__(self):
        self.escursioni_map = {} # Mappa ID escursione -> oggetti Escursione
        self.punti_interesse_map = {} # Mappa ID punto di interesse -> oggetti PuntoInteresse
        self.lista_escursioni = []
        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        # TODO: Aggiungere eventuali altri attributi

        # Caricamento
        self.load_escursioni()
        self.load_lista_escursioni()
        self.load_punti_interesse()
        self.load_relazioni(self.escursioni_map, self.punti_interesse_map)

    @staticmethod
    def load_parchi():
        """ Restituisce tutti i parchi disponibili """
        return ParcoDAO.get_parchi()

    def load_escursioni(self):
        """ Carica tutte le escursioni in un dizionario [id, Escursione]"""
        self.escursioni_map = EscursioneDAO.get_escursioni()

    def load_lista_escursioni(self):
        for escursion in self.escursioni_map:
            self.lista_escursioni.append(escursion)

    def load_punti_interesse(self):
        """ Carica tutti i punti di interesse in un dizionario [id, PuntoInteresse]"""
        self.punti_interesse_map = PuntoInteresseDAO.get_punti_interesse()

    def load_relazioni(self, escursioni, punti_interesse):
        """
            Interroga il database per ottenere tutte le relazioni fra escursioni e punti di interesse e salvarle nelle strutture dati
            Collega escursione <-> punti di interesse.
            --> Ogni Escursione ha un set di PuntoInteresse.
            --> Ogni PuntoInteresse ha un set di Escursioni.
        """
        # TODO
        relazioni = EscursioneDAO.get_escursioni_punti_interesse()
        for escursion in escursioni:
            set_punti_interesse = set()
            for relazione in relazioni:
                for punto_interesse in punti_interesse:
                    if relazione['id_escursione'] == escursion and relazione['id_punto_interesse'] == punto_interesse:
                        set_punti_interesse.add(punto_interesse)
            escursioni[escursion].punti_interesse = set_punti_interesse



    def genera_pacchetto(self, id_parco: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto di escursioni ottimale per un parco rispettando i vincoli di durata, budget e punti di interesse unici.
        :param id_parco: id del parco
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Escursione)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il voto complessivo dei visitatori per il pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        # TODO
        self._ricorsione(0,[], 0, 0, 0, set(), id_parco, max_giorni, max_budget)

        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _ricorsione(self,start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, punti_usati: set,id_parco, max_giorni: int = None, max_budget: float = None):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il voto complessivo dei visitatori"""

        if (max_giorni is not None and durata_corrente > max_giorni) or (max_budget is not None and costo_corrente > max_budget):
            return

        else:
            if valore_corrente > self._valore_ottimo:
                    self._pacchetto_ottimo = copy.deepcopy(pacchetto_parziale)
                    self._costo = costo_corrente
                    self._valore_ottimo = valore_corrente
            for i in range (start_index, len(self.lista_escursioni)):
                escursione = self.lista_escursioni[i]
                if self.escursioni_map[escursione].id_parco == id_parco and self.escursioni_map[escursione].punti_interesse.intersection(punti_usati) == set():
                    pacchetto_parziale.append(self.escursioni_map[escursione])
                    self._ricorsione(start_index + 1, pacchetto_parziale, durata_corrente + int(self.escursioni_map[escursione].durata_giorni), costo_corrente + float(self.escursioni_map[escursione].costo), valore_corrente + sum( float(self.punti_interesse_map[el].voto_visitatori) for el in self.escursioni_map[escursione].punti_interesse), punti_usati.union(self.escursioni_map[escursione].punti_interesse), id_parco, max_giorni, max_budget)
                    pacchetto_parziale.pop()
