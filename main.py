import FreeSimpleGUI as sg
import os
import io
import random
import csv
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

load_dotenv()


class ImageRanker:
    def __init__(self):
        self.image_files = []
        self.folder_path = None
        self.rankings = {}
        self.current_left = None
        self.current_right = None


    def select_folder(self):
        """ Pop-up folder selection for the user to choose the location of images on the filesystem
        """
        folder = sg.popup_get_folder('Image folder to open', default_path='./images')

        if not folder:
            sg.popup_cancel('Canceling')
            raise SystemExit()

        self.folder_path = folder
        self.load_images()
        return len(self.image_files) >= 2
        # create sub list of image files (no sub folders, no wrong file types)
        

    def load_images(self):
        """ Create the list of files from the selected folder
        """
        if not self.folder_path:
            return
        # PIL supported image types
        img_types = ('.png', '.jpg', 'jpeg', '.tiff', '.bmp')
        self.image_files = [
            f for f in os.listdir(self.folder_path) 
            if f.lower().endswith(img_types)
        ]
        
        self.rankings = {img: 0 for img in self.image_files}


    def convert_to_bytes(self, file_path, maxsize=(720, 480)):
        """Generate image data using PIL
        """
        # if not isinstance(file_path, (str, os.PathLike)):
        #     raise TypeError(f'Expected a path, got {type(file_path)}')
        # if not os.path.exists(file_path):
        #     raise FileNotFoundError(f'Image file not found: {file_path}')
        try:
            img = Image.open(file_path)
            img.thumbnail(maxsize)
            
            bio = io.BytesIO()
            img.save(bio, format='PNG')
            del img
            return bio.getvalue()
        except Exception as e:
            sg.popup_error(f'Error loading image: {e}')
            return None


    def get_random_image(self, excludes=None):
        """ Chooses a random image among those in the file list.
            
            Parameters
            excludes : array of str
               the file names of files to exclude from possible return values
        """
        available = [img for img in self.image_files if img not in excludes]
        if not available:
            return None
        return random.choice(available)


    def update_images(self, keep_selected=None, new_random=None):
        """ Update the images in the window
            
            Parameters
            keep_selected : array of str
               string 'right' or 'left' to indicate to keep either image, None will cycle both
            new_random : str
                string filename to set image to, otherwise will select at random
        """
        if keep_selected is None:
            self.current_left, self.current_right = random.sample(self.image_files, 2)
        else:
            if keep_selected == 'left':
                self.current_left = self.current_left
                self.current_right = new_random if new_random else self.get_random_image([self.current_left, self.current_right])
            else:
                self.current_right = self.current_right
                self.current_left = new_random if new_random else self.get_random_image([self.current_left, self.current_right])

        return True


    def record_selection(self, selected_side):
        """ stores vote between images
            
            Parameters
            selected_side : str
               string 'right' or 'left' to indicate to image that was voted for
        """
        if selected_side == 'left':
            selected_image = self.current_left
        else:
            selected_image = self.current_right
        
        if selected_image:
            if selected_image not in self.rankings:
                self.rankings[selected_image] = 0
            self.rankings[selected_image] += 1
    

    def get_ranking_display(self):
        sorted_rankings = sorted(
            self.rankings.items(),
            key=lambda x: x[1],
            reverse=True
        )

        if not sorted_rankings:
            return 'Empty ranking'
        
        max_filename_len = max(len(img) for img, _ in sorted_rankings) if sorted_rankings else 30
        max_filename_len = max(max_filename_len, 20)

        lines = [f"{'Image Filename':<{max_filename_len}} | Votes", "-" * (max_filename_len + 20)]
        
        for rank, (image, votes) in enumerate(sorted_rankings, 1):
            lines.append(f"{image:<{max_filename_len}} | {votes}")
        
        return '\n'.join(lines)
    

    def get_ranking_table_data(self):
        sorted_rankings = sorted(
            self.rankings.items(),
            key=lambda x: x[1],
            reverse=True
        )

        table_data = []
        
        for rank, (image, votes) in enumerate(sorted_rankings, 1):
            table_data.append([rank, image, votes])
        
        return table_data


    def generate_rank_csv(self, header, data):
        """ generates csv of ranking data
            
            Parameters
            header : str
               heading row for csv
            data : array of str
                data for csv entries
        """
        filename = 'rank.csv'

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            writer.writerows(data[0:])

        sg.popup_ok('CSV created successfully!')


    def get_image_eval(self, api_key):
        """ asks Gemini for image evaluation
            
            Parameters
            api_key : str
               Gemini api_key needed for gemini services
        """
        gemini_key = api_key
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel(model_name='gemini-2.5-flash')
        filename = os.path.join(self.folder_path, self.current_left)
        image_for_gemini = Image.open(filename)
        response = model.generate_content(['Rate this image for sharpness on a scale of 0-10', image_for_gemini])
        formatted_text = f'Gemini evaluation for {filename}:\n\n {response.text}'
        layout = [
            [sg.Text(text=formatted_text)],
            [sg.HorizontalSeparator()],
            [
                sg.Button('Copy to Clipboard', key='-COPY_TO_CLIPBOARD-'),
                sg.Button('Close')
            ]
        ]
        window = sg.Window('Gemini - Image Evaluation', layout)

        while True: # 
            sec_event, sec_values = window.read()
            if sec_event == sg.WIN_CLOSED or sec_event == 'Close':
                break
            elif sec_event == '-COPY_TO_CLIPBOARD-':
                sg.clipboard_set(f'Gemini evaluation for {filename}:\n\n {response.text}')
                sg.popup(f'Text copied to clipboard!')

        window.close()
    
    def get_image_comparison(self, api_key, window):
        """ asks Gemini for image evaluation
            
            Parameters
            api_key : str
               Gemini api_key needed for gemini services
            window : simplegui window object
                needed to make call by reference updates to the main window
        """
        gemini_key = api_key
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel(model_name='gemini-2.5-flash')
        file1 = os.path.join(self.folder_path, self.current_left)
        file2 = os.path.join(self.folder_path, self.current_right)
        image1 = Image.open(file1)
        image2 = Image.open(file2)
        response = model.generate_content(['''Compare these two images and indicate which picture is technically superior. 
                                              Start your response with 1 or 2 to indicate which image is the answer before giving details. 
                                              If they are equivalent, randomly select 1 or 2.''', image1, image2])
        formatted_text = f'Gemini comparison for {file1} vs {file2}:\n\n {response.text}'

        if(response.text.startswith('1')):
            sg.popup(f'Gemini voted for image1: {file1}')
            self.record_selection('left')
            self.cycle_image(window, 'right', False)
        else:
            sg.popup(f'Gemini voted for image2: {file2}')
            self.record_selection('right')
            self.cycle_image(window, 'left', False)
        print(f'Gemini full voting response:\n {formatted_text}')
        image1.close()
        image2.close()

    def cycle_image(self, window, side, both):
        """ asks Gemini for image evaluation
            
            Parameters
            window : simplegui window object
                needed to make call by reference updates to the main window
            side : str
                'left' or 'right' for which image to cycle
            both : boolean
                True or False to indicate whether to cycle both images
        """
        keep = 'right'
        if(side.startswith('left')):
            new_img = self.get_random_image([self.current_left, self.current_right])
        else:
            new_img = self.get_random_image([self.current_left, self.current_right])
            keep = 'left'
        if new_img:
            self.update_images(keep_selected=keep, new_random=new_img)
            img1_path = os.path.join(self.folder_path, self.current_left)
            img2_path = os.path.join(self.folder_path, self.current_right)
            img1_data = self.convert_to_bytes(img1_path)
            img2_data = self.convert_to_bytes(img2_path)
            window['-IMAGE1-'].update(data=img1_data)
            window['-IMAGE2-'].update(data=img2_data)
            window['-RANK_TABLE-'].update(values=self.get_ranking_table_data())

        if both:
            self.cycle_image(window, keep, False)

    def run(self):
        api_key = os.getenv('GEMINI_API_KEY')
        ranking_header = ['rank', 'image_name', 'votes']

        if not self.select_folder():
            sg.popup_error('Please select a valid folder')
            return
        
        layout = [
            [
                sg.Column([
                    [sg.Image(key='-IMAGE1-', size=(720, 480), enable_events=True)]
                ], element_justification='center'),
                sg.VSeparator(),
                sg.Column([
                    [sg.Image(key='-IMAGE2-', size=(720, 480), enable_events=True)]
                ], element_justification='center')
            ],
            [sg.HorizontalSeparator()],
            [
                sg.Button('Gemini Eval - left photo', key='-EVAL_LEFT_PHOTO-'),
                sg.Button('Gemini Comparison', key='-COMPARE_PHOTO-'),
                sg.Button('Export ranking to CSV', key='-EXPORT_CSV-'),
                sg.Button('Exit App', key='-EXIT-')
            ],
            [sg.Text('Current Ranking:')],
            [
                sg.Table(
                    values=[],
                    headings=ranking_header,
                    key='-RANK_TABLE-',
                    auto_size_columns=True,
                    num_rows=10,
                    expand_x=True,
                    expand_y=False
                )
            ] 
        ]

        window = sg.Window('Image Ranker', layout, finalize=True, resizable=True)

        if not self.update_images():
            sg.popup_error('No images were found in the selected folder. Exiting.')
            window.close()
            return
        
        if not api_key:
            sg.popup_error('No Gemini Key in .env! Cannot perform AI evaluation.')
            window.close()
            return
        
        img1_path = os.path.join(self.folder_path, self.current_left)
        img2_path = os.path.join(self.folder_path, self.current_right)
        img1_data = self.convert_to_bytes(img1_path)
        img2_data = self.convert_to_bytes(img2_path)
        window['-IMAGE1-'].update(data=img1_data)
        window['-IMAGE2-'].update(data=img2_data)

        window['-RANK_TABLE-'].update(values=self.get_ranking_table_data())

        while True:
            event, values = window.read()

            if event in (sg.WIN_CLOSED, '-EXIT-'):
                break
            elif event == '-IMAGE1-':
                self.record_selection('left')
                self.cycle_image(window, 'right', False)
            elif event == '-IMAGE2-':
                self.record_selection('right')
                self.cycle_image(window, 'left', False)
            elif event == '-EXPORT_CSV-':
                window['-RANK_TABLE-'].update(values=self.get_ranking_table_data())
                self.generate_rank_csv(ranking_header, self.get_ranking_table_data())
            elif event == '-EVAL_LEFT_PHOTO-':
                self.get_image_eval(api_key)
            elif event == '-COMPARE_PHOTO-':
                self.get_image_comparison(api_key, window)
        
        window.close()


def main():
    app = ImageRanker()
    app.run()


if __name__ == '__main__':
    main()
