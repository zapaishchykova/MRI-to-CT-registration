import os
import numpy as np
import itk
import pandas as pd

def register_to_template(
    input_image_path, 
    output_path, 
    fixed_image_path, 
    parameter_object_file,
    create_subfolder=True, 
    image_id_rename=None
):
    """
    Registers the input image to a fixed template using ITK elastix registration.

    Parameters:
        input_image_path (str): Path to the moving image.
        output_path (str): Directory to save the registered image.
        fixed_image_path (str): Path to the fixed image template.
        parameter_object_file (str): Elastix parameter file.
        create_subfolder (bool): Whether to create a subfolder for the output.
        image_id_rename (str): Optional new name for the registered image.
    """
    # Load fixed image
    fixed_image = itk.imread(fixed_image_path, itk.F)

    # Load parameter map
    parameter_object = itk.ParameterObject.New()
    parameter_object.AddParameterFile(parameter_object_file)

    # Process only valid NIfTI files
    if input_image_path.endswith(".nii.gz") and "._" not in input_image_path:
        print(f"Processing: {input_image_path}")

        moving_image = itk.imread(input_image_path, itk.F)

        # Perform registration
        result_image, result_transform_parameters = itk.elastix_registration_method(
            fixed_image, moving_image,
            parameter_object=parameter_object,
            log_to_console=False
        )

        # Configure transformix filter
        transformix_filter = itk.TransformixFilter.New(moving_image)
        transformix_filter.SetTransformParameterObject(result_transform_parameters)
        transformix_filter.SetComputeSpatialJacobian(False)
        transformix_filter.SetComputeDeterminantOfSpatialJacobian(False)
        transformix_filter.SetMovingImage(moving_image)
        transformix_filter.Update()

        transformed_image = transformix_filter.GetOutput()

        print("Fixed image size:", itk.size(fixed_image))
        print("Moving image size:", itk.size(moving_image))
        print("Transformed image size:", itk.size(transformed_image))

        image_id = image_id_rename if image_id_rename else os.path.basename(input_image_path)

        # Save results
        if create_subfolder:
            output_dir = os.path.join(output_path, os.path.splitext(image_id)[0])
            os.makedirs(output_dir, exist_ok=True)
            itk.imwrite(result_image, os.path.join(output_dir, image_id))
        else:
            itk.imwrite(result_image, os.path.join(output_path, image_id))

        print(f"Registered {image_id}")


def find_ct_image(directory):
    """
    Locates a .nii.gz file containing 'CT' in the filename within a directory.

    Parameters:
        directory (str): Path to the directory to search.

    Returns:
        str: Path to the CT file if found, otherwise None.
    """
    for file_name in os.listdir(directory):
        if file_name.endswith(".nii.gz") and "CT" in file_name:
            return os.path.join(directory, file_name)
    return None

def create_larger_image_with_overlay(input_image_path, output_image_path, new_size=(300, 220, 220)):
    """
    Creates a larger image by overlaying the input image onto a blank canvas.

    Parameters:
        input_image_path (str): Path to the input image.
        output_image_path (str): Path to save the output image.
        new_size (tuple): Dimensions of the output image.
    """
    input_image = itk.imread(input_image_path, itk.F)
    input_size = itk.size(input_image)
    input_spacing = input_image.GetSpacing()
    input_origin = input_image.GetOrigin()
    input_direction = input_image.GetDirection()

    print(f"Input image size: {input_size}")

    # Create blank image
    new_image_array = np.zeros(new_size, dtype=np.float32)
    new_image = itk.image_from_array(new_image_array)
    new_image.SetSpacing(input_spacing)
    new_image.SetOrigin(input_origin)
    new_image.SetDirection(input_direction)

    print(f"New image size: {new_size}")

    # Trim input image and overlay onto blank image
    input_array = itk.GetArrayFromImage(input_image)[:-1, :, :]
    input_array[input_array > 9000] = 0
    z_offset = new_size[0] - input_array.shape[0]
    new_image_array[z_offset:, :input_size[1], :input_size[0]] = input_array

    # Save the output image
    itk.imwrite(new_image, output_image_path)
    print(f"Larger image saved to {output_image_path}")

# Paths and parameters
elastix_params_mri = "par_rigid_mri.txt"
elastix_params_ct = "par_ct.txt"
elastix_params_ct_2 = "rigid.txt"

input_path = "data/mri_ct/"
save_to = "data/registered_mri_ct/"
template_mri = "MNI152_T1_1mm_padded.nii.gz"
template_ct = "bone_padded.nii.gz"

# Process input files
for subject_dir in os.listdir(input_path):
    subject_path = os.path.join(input_path, subject_dir)
    for file_name in os.listdir(subject_path):
        if file_name.endswith(".nii.gz") and "MR" in file_name:
            mri_file = os.path.join(subject_path, file_name)

            csv_file_path = os.path.join(subject_path, file_name.replace(".nii.gz", ".csv"))
            df = pd.read_csv(csv_file_path, header=None)

            # Extract MRN from CSV file
            mrn = df[df[2].str.contains("Patient ID")][4].values[0]
            output_dir = os.path.join(save_to, mrn)
            os.makedirs(output_dir, exist_ok=True)

            # Register MRI to template
            register_to_template(mri_file, output_dir, template_mri, elastix_params_mri,
                                 create_subfolder=False, image_id_rename=f"{mrn}_MR.nii")
            registered_mri_file = os.path.join(output_dir, f"{mrn}_MR.nii")

            # Locate corresponding CT file
            ct_file = find_ct_image(subject_path)

            # Register CT to MRI and templates
            if ct_file:
                register_to_template(ct_file, output_dir, template_ct, elastix_params_ct,
                                     create_subfolder=False, image_id_rename=f"{mrn}_CT.nii")

                ct_registered_to_mri = os.path.join(output_dir, f"{mrn}_CT.nii")
                register_to_template(ct_registered_to_mri, output_dir, registered_mri_file, elastix_params_ct_2,
                                     create_subfolder=False, image_id_rename=f"{mrn}_CT2.nii")
            else:
                print(f"CT file not found for {mri_file}")
            break
