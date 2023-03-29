"""
WallConstruction Multithreading Simulation

"""
import logging
import queue
import time
from .base import BaseWallConstruction, Workload
from threading import Thread
from typing import Optional
from enum import Enum


class TeamWorker(Thread):
    """
    Represents Team worker thread
    """

    class ThreadStatus(Enum):
        AWAITING = 0
        BUSY = 1
        RELIEVED = 2

    def __init__(self, idx: int, w_queue: queue.Queue, logger: logging.Logger, day: int = None):
        """
         :param idx: Team index
         :param w_queue: Workload queue
         :param day: Day to stop work
         :param logger: Worker logger
         """
        self.idx = idx
        self.queue = w_queue
        self.stop_day = day
        self.logger = logger

        self.status: TeamWorker.ThreadStatus = TeamWorker.ThreadStatus.AWAITING
        self.workload: Optional[Workload] = None
        self.day = 1
        self.received_task_day = 0

        super().__init__()

    def relieve(self):
        self.status = self.ThreadStatus.RELIEVED
        self.log(f'[Day - {self.day}] [Team {self.idx}] Relieved.')

        # Commit Day even if relieved
        self.day += 1

        # Finish If section unfinished
        try:
            self.queue.task_done()
        except:
            pass

    def log(self, msg: str):
        self.logger.debug(msg)

    def run(self):
        current_section_height = 0

        while True:

            if self.status == self.ThreadStatus.AWAITING:
                self.workload = self.queue.get()
                self.log(f'[Day - {self.day}] [Team {self.idx}] Got workload {self.workload}')

                if self.workload.is_relieve:
                    return self.relieve()

                current_section_height = self.workload.section_height
                self.received_task_day = self.day
                self.status = self.ThreadStatus.BUSY

            current_section_height += BaseWallConstruction.FOOTS_PER_DAY

            self.log(f'[Day - {self.day}] [Team {self.idx}]  Profile {self.workload.profile + 1}'
                     f' Section {self.workload.section + 1}'
                     f' Height {current_section_height}')

            if current_section_height == BaseWallConstruction.SECTION_HEIGHT:
                self.log(f'[Day - {self.day}] [Team {self.idx}]  Completed section {self.workload.section + 1} '
                         f'in profile {self.workload.profile + 1}')
                self.status = self.ThreadStatus.AWAITING
                self.day += 1
                self.queue.task_done()
                continue

            if self.day == self.stop_day:
                self.log(f'[Day - {self.day}] [Team {self.idx}]  Stop day reached Queue {self.queue.qsize()}')
                return self.relieve()

            self.day += 1


class WallConstructionMt(BaseWallConstruction):
    """
    Represents Manager thread
    """
    RELIEVE_WORKLOAD = Workload(is_relieve=True)

    def __init__(self, file_input: str, log_file: str = ''):

        f = open(file_input, "r")
        self.available_teams = int(f.readline())

        super().__init__(f)

        if not log_file:
            log_file = f'wallconstruction/logs/mt/worker_out_{time.time()}.log'

        fileh = logging.FileHandler(log_file, 'w')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fileh.setFormatter(formatter)

        self.worker_logger = logging.getLogger('AsyncWorkerLogger')
        self.worker_logger.setLevel(logging.DEBUG)
        self.worker_logger.addHandler(fileh)

        self.work_queue = queue.Queue(maxsize=self.available_teams)
        self.workers_pool = [TeamWorker(idx=i, w_queue=self.work_queue, logger=self.worker_logger)
                             for i in range(self.available_teams)]

    def get_wall_costs(self,
                       profile_no: Optional[int] = None,
                       day: Optional[int] = None,
                       accumulate: Optional[bool] = False) -> (int, int):

        total_workload_in_foots = 0
        processed_volume = 0
        current_day_volume = 0
        profile_no = profile_no - 1 if profile_no else None

        for profile in self.wall_profiles:
            for section in profile:
                total_workload_in_foots += self.SECTION_HEIGHT - section

        workflow = self.workflow_gen()

        for worker in self.workers_pool:
            worker.stop_day = day
            worker.start()

        while processed_volume != total_workload_in_foots * self.ICE_VOLUME_PER_FOOT:

            current_day_volume = 0

            # Set workload for available workers
            for idx, worker in enumerate(self.workers_pool):
                if worker.status == TeamWorker.ThreadStatus.AWAITING:
                    try:
                        workload = next(workflow)
                    except StopIteration:
                        workload = self.RELIEVE_WORKLOAD

                    self.work_queue.put(workload)

            self.work_queue.join()

            for worker in self.workers_pool:
                worker_profile = worker.workload.profile
                worker_section = worker.workload.section

                if worker_profile is None:
                    continue

                section_height_delta = self.SECTION_HEIGHT - self.wall_profiles[worker_profile][worker_section]

                if profile_no is not None and profile_no != worker_profile:
                    continue
                if day:
                    days_worked_on_profile = day - worker.received_task_day + 1
                    processed_volume += days_worked_on_profile * self.ICE_VOLUME_PER_FOOT \
                        if days_worked_on_profile > 0 else self.ICE_VOLUME_PER_FOOT
                    current_day_volume += self.ICE_VOLUME_PER_FOOT
                else:
                    processed_volume += section_height_delta * self.ICE_VOLUME_PER_FOOT

            # Check if passed all requested profile was finished among all workers
            if profile_no is not None and all(profile_no < worker.workload.profile for worker in self.workers_pool):
                break

            # Check if passed worker day was stop day
            if day and all(day == worker.day - 1 for worker in self.workers_pool):
                break

        # Relieve rest teams
        for worker in self.workers_pool:
            if worker.status != TeamWorker.ThreadStatus.RELIEVED:
                self.work_queue.put(self.RELIEVE_WORKLOAD)

        self.work_queue.join()
        return (processed_volume, processed_volume * self.COST_PER_ICE_VOLUME) if accumulate else \
            (current_day_volume, current_day_volume * self.COST_PER_ICE_VOLUME)
