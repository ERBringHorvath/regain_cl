from django.shortcuts import render, redirect
from django.conf import settings
from django.core.mail import send_mail
from django.views.generic.edit import FormView
from .models import FastaFileUpload
from .forms import FastaFileForm
from django.http import FileResponse, HttpResponse
import os, glob, zipfile, logging, shutil
from .amrfinder_analysis import run_amrfinder_analysis, combine_output_files, create_matrix 
from .amrfinder_analysis import process_amrfinder_files
from django.urls import reverse
from django_celery_results.models import TaskResult
from django.contrib.sites.models import Site
from celery import group, chain, chord, shared_task

##Get log information from specific points in each program
logger = logging.getLogger('data_acquisition')
logger.debug('This is a debug message')


class FastaFileFormView(FormView):
    form_class = FastaFileForm
    template_name = 'data_acquisition/upload.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get task information
        context['all_tasks'] = TaskResult.objects.all().count()
        context['running_tasks'] = TaskResult.objects.filter(status='STARTED').count()
        context['pending_tasks'] = TaskResult.objects.filter(status='PENDING').count()

        return context
    
    def form_valid(self, form):
        logger.debug('form_valid method started')

        # Save the form to create a FastaFileUpload instance
        fasta_instance = form.save()
        logger.debug(f'FastaFileUpload instance created with ID {fasta_instance.id}')

        upload_timestamp = fasta_instance.upload_timestamp
        logger.debug(f'FastaFileUpload instance timestamp: {upload_timestamp}')

        ###Non-chord calling
        #Gather file paths from the saved files
        file_paths = [fasta_file.file.path for fasta_file in fasta_instance.fasta_files.all()]
        logger.debug(f'Files to process: {file_paths}, {upload_timestamp}')

        user_email = fasta_instance.email

        task = process_amrfinder_files.delay(
            file_paths,
            fasta_instance.organism,
            fasta_instance.gene_type,
            fasta_instance.min_gene_occurrence,
            fasta_instance.max_gene_occurrence,
            upload_timestamp,
            fasta_instance.simplify_gene_names,
            email=user_email,
            site_domain=Site.objects.get_current().domain,
            fasta_instance_id=fasta_instance.id
        )

        logger.debug(f'form_valid method finished {upload_timestamp}')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('home:success')


def download_results_view(request, upload_id):
    try:
        upload = FastaFileUpload.objects.get(id=upload_id)
    except FastaFileUpload.DoesNotExist:
        return HttpResponse("Requested Data Not Found", status=404)
    # Construct the directory path using the upload timestamp
    results_dir = os.path.join(settings.MEDIA_ROOT, f"fasta_files/{upload.upload_timestamp}")

    # List all relevant files in this directory
    result_files = glob.glob(os.path.join(results_dir, "*"))

    # Create a zip file to contain all the result files
    zip_file_path = os.path.join(settings.MEDIA_ROOT, f'amrfinder_results_{upload.upload_timestamp}.zip')
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for file_path in result_files:
            zipf.write(file_path, os.path.basename(file_path))

    # Send the zip file as the response
    if os.path.exists(zip_file_path):
        return FileResponse(open(zip_file_path, 'rb'), as_attachment=True)
    else:
        return HttpResponse("Unable to create zip file.", status=500)

def tasks_info(request):
    logger.debug("tasks_info called")
    print("tasks_info called")
    ##All submited tasks
    all_tasks = TaskResult.objects.all().count()

    ##Current tasks
    running_tasks = TaskResult.objects.filter(status='STARTED').count()

    ##Queued tasks
    pending_tasks = TaskResult.objects.filter(status='PENDING').count()

    context = {
        'all_tasks': all_tasks,
        'running_tasks': running_tasks,
        'pending_tasks': pending_tasks,
    }

    print(all_tasks, running_tasks, pending_tasks)

    return render(request, 'data_acquisition/data_acquisition.html', context)